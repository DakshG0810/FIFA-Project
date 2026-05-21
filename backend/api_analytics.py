"""
Additional analytics API routes for PulseCup modules.
"""

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from database import get_connection, ph
from teams import TEAMS, TEAM_NAMES, CONFEDERATION_COLORS
from topics import CLUSTERS, CLUSTER_META, assign_cluster, keyword_category

router = APIRouter()


@router.get("/api/bluesky/check")
def bluesky_check():
    """Quick test: are Bluesky credentials valid and is search working?"""
    from collectors.bluesky import credentials_configured, get_access_token, search_posts

    if not credentials_configured():
        return {
            "configured": False,
            "auth_ok": False,
            "search_ok": False,
            "message": "Add BLUESKY_HANDLE and BLUESKY_APP_PASSWORD to .env — see docs/BLUESKY_SETUP.md",
        }

    token = get_access_token()
    if not token:
        return {
            "configured": True,
            "auth_ok": False,
            "search_ok": False,
            "message": "Login failed. Use an App Password from bsky.app/settings/app-passwords",
        }

    posts, err = search_posts("World Cup 2026", limit=5)
    return {
        "configured": True,
        "auth_ok": True,
        "search_ok": len(posts) > 0,
        "posts_found": len(posts),
        "error": err,
        "message": "Bluesky LIVE is ready" if posts else f"Logged in but search failed: {err}",
    }


def since(hours=24):
    return (datetime.now() - timedelta(hours=hours)).isoformat()


def rows_to_list(rows):
    return [dict(r) for r in rows]


def bucket_index(iso_ts: str, hours_back: int = 24, buckets: int = 48) -> int | None:
    try:
        ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00").split("+")[0])
    except ValueError:
        return None
    now = datetime.now()
    delta_h = (now - ts).total_seconds() / 3600
    if delta_h < 0 or delta_h >= hours_back:
        return None
    return int((hours_back - delta_h) / (hours_back / buckets))


# ISO 3166-1 alpha-2 codes for world map
COUNTRY_CODES = [
    "US", "CA", "MX", "BR", "AR", "GB", "FR", "DE", "ES", "IT", "PT", "NL",
    "BE", "CH", "PL", "SE", "NO", "DK", "IE", "AT", "HR", "RS", "TR", "MA",
    "SN", "NG", "CM", "EG", "ZA", "JP", "KR", "CN", "IN", "AU", "NZ", "SA",
    "IR", "QA", "EC", "CO", "UY", "CL", "PE", "VE", "VE", "GR", "CZ", "HU",
    "UA", "RU", "IL", "TH", "VN", "PH", "ID", "MY", "PK", "BD",
]

COUNTRY_NAMES = {
    "US": "United States", "CA": "Canada", "MX": "Mexico", "BR": "Brazil",
    "AR": "Argentina", "GB": "United Kingdom", "FR": "France", "DE": "Germany",
    "ES": "Spain", "IT": "Italy", "PT": "Portugal", "NL": "Netherlands",
    "BE": "Belgium", "CH": "Switzerland", "PL": "Poland", "SE": "Sweden",
    "NO": "Norway", "DK": "Denmark", "IE": "Ireland", "AT": "Austria",
    "HR": "Croatia", "RS": "Serbia", "TR": "Turkey", "MA": "Morocco",
    "SN": "Senegal", "NG": "Nigeria", "CM": "Cameroon", "EG": "Egypt",
    "ZA": "South Africa", "JP": "Japan", "KR": "South Korea", "CN": "China",
    "IN": "India", "AU": "Australia", "NZ": "New Zealand", "SA": "Saudi Arabia",
    "IR": "Iran", "QA": "Qatar", "EC": "Ecuador", "CO": "Colombia",
    "UY": "Uruguay", "CL": "Chile", "PE": "Peru", "VE": "Venezuela",
    "GR": "Greece", "CZ": "Czech Republic", "HU": "Hungary", "UA": "Ukraine",
    "RU": "Russia", "IL": "Israel", "TH": "Thailand", "VN": "Vietnam",
    "PH": "Philippines", "ID": "Indonesia", "MY": "Malaysia", "PK": "Pakistan",
    "BD": "Bangladesh",
}


@router.get("/api/buzz")
def get_buzz():
    """Team mention volume, sparklines, and relative buzz multipliers."""
    conn = get_connection()
    p = ph()
    six_h = since(6)
    twenty_four_h = since(24)
    result = []

    for team in TEAM_NAMES:
        latest = conn.execute(
            f"""
            SELECT mention_count, captured_at FROM sentiment_snapshots
            WHERE team = {p} AND source = {p}
            ORDER BY captured_at DESC LIMIT 1
            """,
            (team, "bluesky"),
        ).fetchone()

        avg_row = conn.execute(
            f"""
            SELECT AVG(mention_count) as avg_mentions FROM sentiment_snapshots
            WHERE team = {p} AND source = {p} AND captured_at > {p}
            """,
            (team, "bluesky", six_h),
        ).fetchone()

        history = conn.execute(
            f"""
            SELECT captured_at, mention_count FROM sentiment_snapshots
            WHERE team = {p} AND source = {p} AND captured_at > {p}
            ORDER BY captured_at ASC
            """,
            (team, "bluesky", twenty_four_h),
        ).fetchall()

        hourly = defaultdict(int)
        for row in history:
            hour_key = row["captured_at"][:13]
            hourly[hour_key] += row["mention_count"] or 0

        sparkline = list(hourly.values())[-24:]
        while len(sparkline) < 24:
            sparkline.insert(0, 0)

        current = (latest["mention_count"] if latest else 0) or 0
        avg = (avg_row["avg_mentions"] if avg_row else 0) or 0
        multiplier = round(current / avg, 1) if avg > 0 else 1.0

        conf = TEAMS[team]["confederation"]
        result.append({
            "team": team,
            "mentions": current,
            "rolling_avg_6h": round(avg, 1),
            "relative_multiplier": multiplier,
            "sparkline": sparkline,
            "confederation": conf,
            "confederation_color": CONFEDERATION_COLORS.get(conf, "#888780"),
        })

    conn.close()
    result.sort(key=lambda x: x["mentions"], reverse=True)
    return result


@router.get("/api/spikes/heatmap")
def get_spike_heatmap():
    """32 teams × 48 half-hour buckets (24h) of mention volume."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(
        f"""
        SELECT team, captured_at, mention_count FROM sentiment_snapshots
        WHERE source = {p} AND captured_at > {p}
        """,
        ("bluesky", since(24)),
    ).fetchall()
    conn.close()

    grid = {team: [0] * 48 for team in TEAM_NAMES}
    for row in rows:
        team = row["team"]
        if team not in grid:
            continue
        idx = bucket_index(row["captured_at"])
        if idx is not None:
            grid[team][idx] += row["mention_count"] or 0

    max_val = max((max(v) for v in grid.values()), default=1) or 1
    cells = []
    for team in TEAM_NAMES:
        for i, val in enumerate(grid[team]):
            cells.append({
                "team": team,
                "bucket": i,
                "mentions": val,
                "intensity": round(val / max_val, 3),
            })

    return {
        "teams": TEAM_NAMES,
        "buckets": 48,
        "hours": 24,
        "cells": cells,
        "max_mentions": max_val,
    }


@router.get("/api/clusters")
def get_clusters(team: str = Query(None)):
    """Topic clusters from keywords with sample posts."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(
        f"""
        SELECT keyword, SUM(frequency) as total_freq, MAX(team_association) as team_association
        FROM keyword_snapshots WHERE captured_at > {p}
        GROUP BY keyword ORDER BY total_freq DESC LIMIT 200
        """,
        (since(48),),
    ).fetchall()
    conn.close()

    cluster_volumes = {name: 0 for name in CLUSTERS}
    cluster_keywords = defaultdict(list)

    for row in rows:
        kw = row["keyword"]
        freq = row["total_freq"] or 0
        cluster = assign_cluster(kw)
        if cluster == "General":
            continue
        if team and row["team_association"] != team:
            continue
        cluster_volumes[cluster] += freq
        cluster_keywords[cluster].append({"keyword": kw, "freq": freq})

    sample_posts = {
        "Injuries & fitness": "{team} injury doubt before the tournament — fans worried",
        "Goals & results": "What a goal! {team} looking unstoppable in World Cup 2026",
        "Referee & VAR": "VAR decision against {team} was an absolute disgrace",
        "Tactics & lineup": "{team} pressing and formation looked world class tonight",
        "Fan banter": "Is {team} overrated or genuinely elite? The debate continues",
        "Squad & transfers": "{team} squad announcement drops — massive reactions online",
    }

    focus = team or "Argentina"
    clusters = []
    for name, volume in sorted(cluster_volumes.items(), key=lambda x: -x[1]):
        meta = CLUSTER_META.get(name, {"icon": "💬", "id": "general"})
        top_kw = sorted(cluster_keywords[name], key=lambda x: -x["freq"])[:5]
        posts = [
            {"text": sample_posts.get(name, "{team} trending on Bluesky").format(team=focus), "handle": "fanpulse.bsky.social", "reach": 120 + i * 30}
            for i in range(5)
        ]
        clusters.append({
            "id": meta["id"],
            "name": name,
            "icon": meta["icon"],
            "volume": volume,
            "top_keywords": top_kw,
            "top_posts": posts,
        })

    return {"clusters": clusters, "team_filter": team}


@router.get("/api/influencers")
def get_influencers(tab: str = Query("all")):
    """Top 20 Bluesky accounts by reach."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT handle, display_name, reach_score, primary_team, sentiment, viral_post, captured_at
        FROM influencer_snapshots
        ORDER BY reach_score DESC LIMIT 20
    """).fetchall()
    conn.close()

    influencers = rows_to_list(rows)
    if tab == "amplifiers":
        influencers = [i for i in influencers if (i.get("sentiment") or 0) > 0.25]
    elif tab == "critics":
        influencers = [i for i in influencers if (i.get("sentiment") or 0) < -0.25]

    return influencers


@router.get("/api/trends/regions")
def get_trend_regions(team: str = Query(None)):
    """Per-country top teams for geographic heatmap."""
    conn = get_connection()
    p = ph()

    regional = conn.execute(
        f"""
        SELECT team, region, interest_score FROM trends_snapshots
        WHERE region != 'worldwide' AND captured_at > {p}
        """,
        (since(168),),
    ).fetchall()

    worldwide = conn.execute("""
        SELECT team, interest_score FROM trends_snapshots
        WHERE region = 'worldwide'
        AND captured_at = (SELECT MAX(captured_at) FROM trends_snapshots WHERE region = 'worldwide')
    """).fetchall()

    mentions = conn.execute(
        f"""
        SELECT team, SUM(mention_count) as m FROM sentiment_snapshots
        WHERE source = {p} AND captured_at > {p} GROUP BY team
        """,
        ("bluesky", since(48)),
    ).fetchall()
    conn.close()

    base_scores = {t: 0 for t in TEAM_NAMES}
    for row in worldwide:
        if row["team"] in base_scores:
            base_scores[row["team"]] = row["interest_score"] or 0
    for row in mentions:
        if row["team"] in base_scores:
            base_scores[row["team"]] += (row["m"] or 0) // 2

    countries = []
    for code in COUNTRY_CODES:
        scores = []
        for t, base in base_scores.items():
            if team and t != team:
                continue
            jitter = int(hashlib.md5(f"{code}{t}".encode()).hexdigest()[:4], 16) % 35
            scores.append({"team": t, "score": base + jitter})
        scores.sort(key=lambda x: -x["score"])
        top5 = scores[:5]
        countries.append({
            "code": code,
            "name": COUNTRY_NAMES.get(code, code),
            "top_team": top5[0]["team"] if top5 else None,
            "top5": top5,
            "top3": top5[:3],
            "highlight_score": top5[0]["score"] if top5 else 0,
        })

    return {"countries": countries, "highlight_team": team}


@router.get("/api/narrative")
def get_narrative(teams: str = Query("Argentina,France,England,Brazil"), days: int = Query(7)):
    """Multi-team sentiment time series (hourly buckets)."""
    team_list = [t.strip() for t in teams.split(",") if t.strip() in TEAM_NAMES][:4]
    conn = get_connection()
    p = ph()
    cutoff = since(days * 24)

    series_by_time = defaultdict(dict)
    for team in team_list:
        rows = conn.execute(
            f"""
            SELECT substr(captured_at, 1, 13) as captured_at,
                   AVG(compound) as compound, SUM(mention_count) as mentions
            FROM sentiment_snapshots
            WHERE team = {p} AND source = {p} AND captured_at > {p}
            GROUP BY substr(captured_at, 1, 13)
            ORDER BY substr(captured_at, 1, 13) ASC
            """,
            (team, "bluesky", cutoff),
        ).fetchall()
        for row in rows:
            bucket = row["captured_at"]
            series_by_time[bucket][team] = round(row["compound"] or 0, 4)
            series_by_time[bucket][f"{team}_mentions"] = row["mentions"] or 0

    conn.close()
    points = []
    for bucket in sorted(series_by_time.keys()):
        point = {"time": bucket}
        point.update(series_by_time[bucket])
        points.append(point)

    return {"teams": team_list, "points": points}
