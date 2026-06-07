"""
Additional analytics API routes for PulseCup modules.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from database import get_connection, ph
from geo_regions import COUNTRY_CODES, COUNTRY_NAMES
from teams import TEAMS, TEAM_NAMES, CONFEDERATION_COLORS
from topics import CLUSTERS, CLUSTER_META, assign_cluster, is_bot_post, is_wc_post_text

DEMO_HANDLE_RE = re.compile(r"^fan\d+\.bsky\.social$", re.I)
CONVERGENCE_TOP_N = 12
CONVERGENCE_MAX_GAP = 4
DIVERGENCE_MIN_GAP = 5

router = APIRouter()


def _latest_valid_odds_capture(conn, min_teams: int = 25):
    rows = conn.execute(f"""
        SELECT captured_at, SUM(win_probability) AS total_prob
        FROM odds_snapshots
        GROUP BY captured_at
        HAVING COUNT(DISTINCT team) >= {min_teams}
        ORDER BY captured_at DESC
    """).fetchall()
    for row in rows:
        if ((row["total_prob"] if row else 0) or 0) > 1.05:
            return row["captured_at"]
    return None


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


def rank_by_value(items: list[tuple[str, float]], reverse: bool = True) -> dict[str, int]:
    """Return team → rank (1 = best)."""
    ordered = sorted(items, key=lambda x: x[1], reverse=reverse)
    return {team: i + 1 for i, (team, _) in enumerate(ordered)}


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
    """48 teams × one column per collection day (Bluesky mention volume)."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(
        f"""
        SELECT team, captured_at, mention_count FROM sentiment_snapshots
        WHERE source = {p}
        ORDER BY captured_at ASC
        """,
        ("bluesky",),
    ).fetchall()
    conn.close()

    if not rows:
        return {
            "teams": TEAM_NAMES,
            "buckets": 0,
            "dates": [],
            "cells": [],
            "max_mentions": 1,
        }

    # One column per day we actually collected (grows +1 after each daily GitHub Action run)
    dates = sorted({row["captured_at"][:10] for row in rows})
    date_idx = {d: i for i, d in enumerate(dates)}
    grid = {team: [0] * len(dates) for team in TEAM_NAMES}
    for row in rows:
        team = row["team"]
        day = row["captured_at"][:10]
        if team not in grid or day not in date_idx:
            continue
        grid[team][date_idx[day]] += row["mention_count"] or 0

    max_val = max((max(v) for v in grid.values()), default=1) or 1
    cells = []
    for team in TEAM_NAMES:
        for i, val in enumerate(grid[team]):
            cells.append({
                "team": team,
                "bucket": i,
                "mentions": val,
                "intensity": round(val / max_val, 3) if max_val else 0,
            })

    return {
        "teams": TEAM_NAMES,
        "buckets": len(dates),
        "dates": dates,
        "first_collection_date": dates[0] if dates else None,
        "last_collection_date": dates[-1] if dates else None,
        "cells": cells,
        "max_mentions": max_val,
    }


@router.get("/api/clusters")
def get_clusters(team: str = Query(None)):
    """Topic clusters from Bluesky keywords and real stored posts."""
    conn = get_connection()
    p = ph()
    latest_day_row = conn.execute(
        "SELECT MAX(substr(captured_at, 1, 10)) as d FROM cluster_posts"
    ).fetchone()
    latest_day = (latest_day_row["d"] if latest_day_row else None) or ""
    cutoff = since(72)
    rows = conn.execute(
        f"""
        SELECT keyword, SUM(frequency) as total_freq, MAX(team_association) as team_association
        FROM keyword_snapshots
        WHERE captured_at > {p} AND source = {p}
        GROUP BY keyword ORDER BY total_freq DESC LIMIT 200
        """,
        (cutoff, "bluesky"),
    ).fetchall()

    if latest_day:
        post_rows = conn.execute(
            f"""
            SELECT cluster, team, handle, display_name, text, reach, post_uri
            FROM cluster_posts
            WHERE substr(captured_at, 1, 10) = {p}
            ORDER BY reach DESC
            """,
            (latest_day,),
        ).fetchall()
    else:
        post_rows = conn.execute(
            f"""
            SELECT cluster, team, handle, display_name, text, reach, post_uri
            FROM cluster_posts
            WHERE captured_at > {p}
            ORDER BY reach DESC
            """,
            (cutoff,),
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

    cluster_posts: dict[str, list] = defaultdict(list)
    seen_posts: dict[str, set[str]] = defaultdict(set)
    for row in post_rows:
        cluster = row["cluster"]
        if cluster not in CLUSTERS:
            continue
        if team and row["team"] != team:
            continue
        text = row["text"] or ""
        handle = row["handle"] or ""
        if is_bot_post(text, handle) or not is_wc_post_text(text):
            continue
        dedupe = row["post_uri"] or text[:200]
        if dedupe in seen_posts[cluster]:
            continue
        seen_posts[cluster].add(dedupe)
        cluster_posts[cluster].append({
            "text": row["text"],
            "handle": row["handle"],
            "reach": row["reach"] or 0,
        })
        cluster_volumes[cluster] += 1

    clusters = []
    for name in CLUSTERS:
        volume = cluster_volumes[name]
        meta = CLUSTER_META.get(name, {"icon": "💬", "id": "general"})
        top_kw = sorted(cluster_keywords[name], key=lambda x: -x["freq"])[:5]
        top_posts = cluster_posts[name][:5]
        clusters.append({
            "id": meta["id"],
            "name": name,
            "icon": meta["icon"],
            "volume": volume,
            "top_keywords": top_kw,
            "top_posts": top_posts,
        })

    clusters.sort(key=lambda x: -x["volume"])
    return {"clusters": clusters, "team_filter": team}


@router.get("/api/influencers")
def get_influencers(tab: str = Query("all")):
    """Top Bluesky accounts by reach on WC-related posts (likes + reposts)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT handle, display_name, reach_score, primary_team, sentiment, viral_post, captured_at
        FROM influencer_snapshots
        ORDER BY reach_score DESC LIMIT 40
    """).fetchall()
    conn.close()

    influencers = []
    for row in rows_to_list(rows):
        handle = row.get("handle") or ""
        if DEMO_HANDLE_RE.match(handle):
            continue
        if not is_wc_post_text(row.get("viral_post") or ""):
            continue
        influencers.append(row)
        if len(influencers) >= 20:
            break

    if tab == "amplifiers":
        influencers = [i for i in influencers if (i.get("sentiment") or 0) > 0.25]
    elif tab == "critics":
        influencers = [i for i in influencers if (i.get("sentiment") or 0) < -0.25]

    return influencers


def _build_country_team_scores(
    country_code: str,
    regional: dict[str, dict[str, int]],
    team_filter: str | None,
) -> tuple[list[dict], bool]:
    """Rank teams using Google Trends geo data for that country only — no worldwide fallback."""
    regional_scores = regional.get(country_code, {})
    if not regional_scores:
        return [], False

    scores: list[dict] = []
    for t in TEAM_NAMES:
        if team_filter and t != team_filter:
            continue
        score = regional_scores.get(t, 0)
        if score > 0:
            scores.append({"team": t, "score": score})

    scores.sort(key=lambda x: -x["score"])
    return scores, True


@router.get("/api/trends/regions")
def get_trend_regions(team: str = Query(None)):
    """Per-country Google Trends search interest (no Bluesky)."""
    conn = get_connection()
    p = ph()

    regional_rows = conn.execute(
        f"""
        SELECT team, region, interest_score, captured_at FROM trends_snapshots
        WHERE region != 'worldwide' AND captured_at > {p}
        """,
        (since(336),),
    ).fetchall()

    conn.close()

    regional: dict[str, dict[str, int]] = defaultdict(dict)
    latest_capture: dict[str, str] = {}
    for row in regional_rows:
        region = row["region"]
        t = row["team"]
        if t not in TEAM_NAMES:
            continue
        cap = row["captured_at"] or ""
        if region not in latest_capture or cap > latest_capture[region]:
            latest_capture[region] = cap
            regional[region] = {}
        if cap == latest_capture[region]:
            regional[region][t] = max(regional[region].get(t, 0), row["interest_score"] or 0)

    countries = []
    with_data = 0
    for code in COUNTRY_CODES:
        ranked, has_regional = _build_country_team_scores(code, regional, team)
        top5 = ranked[:5]
        if has_regional:
            with_data += 1
        countries.append({
            "code": code,
            "name": COUNTRY_NAMES.get(code, code),
            "has_regional_data": has_regional,
            "top_team": top5[0]["team"] if top5 else None,
            "top5": top5,
            "top3": top5[:3],
            "highlight_score": top5[0]["score"] if top5 else 0,
        })

    return {
        "countries": countries,
        "highlight_team": team,
        "countries_with_data": with_data,
        "countries_total": len(COUNTRY_CODES),
    }


@router.get("/api/narrative")
def get_narrative(teams: str = Query("Argentina,France,England,Brazil")):
    """Multi-team sentiment time series — one point per collection day."""
    team_list = [t.strip() for t in teams.split(",") if t.strip() in TEAM_NAMES][:4]
    conn = get_connection()
    p = ph()

    earliest = conn.execute(
        f"""
        SELECT MIN(captured_at) as first_at FROM sentiment_snapshots WHERE source = {p}
        """,
        ("bluesky",),
    ).fetchone()
    cutoff = (earliest["first_at"] if earliest and earliest["first_at"] else since(7 * 24))

    series_by_day = defaultdict(dict)
    for team in team_list:
        rows = conn.execute(
            f"""
            SELECT substr(captured_at, 1, 10) as day,
                   AVG(compound) as compound, SUM(mention_count) as mentions
            FROM sentiment_snapshots
            WHERE team = {p} AND source = {p} AND captured_at >= {p}
            GROUP BY substr(captured_at, 1, 10)
            ORDER BY day ASC
            """,
            (team, "bluesky", cutoff),
        ).fetchall()
        for row in rows:
            day = row["day"]
            series_by_day[day][team] = round(row["compound"] or 0, 4)
            series_by_day[day][f"{team}_mentions"] = row["mentions"] or 0

    conn.close()
    points = []
    for day in sorted(series_by_day.keys()):
        point = {"time": day}
        point.update(series_by_day[day])
        points.append(point)

    return {
        "teams": team_list,
        "points": points,
        "first_collection_date": cutoff[:10] if cutoff else None,
    }


@router.get("/api/interest-odds")
def get_interest_odds():
    """Odds rank vs combined Google Trends + Bluesky interest rank."""
    conn = get_connection()
    p = ph()

    trends_rows = conn.execute("""
        SELECT team, interest_score FROM trends_snapshots
        WHERE region = 'worldwide'
        AND captured_at = (SELECT MAX(captured_at) FROM trends_snapshots WHERE region = 'worldwide')
    """).fetchall()

    mention_rows = conn.execute(
        f"""
        SELECT team, SUM(mention_count) as mentions
        FROM sentiment_snapshots WHERE source = {p}
        GROUP BY team
        """,
        ("bluesky",),
    ).fetchall()

    latest_odds = _latest_valid_odds_capture(conn)
    if latest_odds:
        odds_rows = conn.execute(
            f"SELECT team, win_probability FROM odds_snapshots WHERE captured_at = {p}",
            (latest_odds,),
        ).fetchall()
    else:
        odds_rows = []
    conn.close()

    trends_map = {t: 0 for t in TEAM_NAMES}
    for row in trends_rows:
        if row["team"] in trends_map:
            trends_map[row["team"]] = row["interest_score"] or 0

    mentions_map = {t: 0 for t in TEAM_NAMES}
    for row in mention_rows:
        if row["team"] in mentions_map:
            mentions_map[row["team"]] = row["mentions"] or 0

    odds_map = {t: 0.0 for t in TEAM_NAMES}
    for row in odds_rows:
        if row["team"] in odds_map:
            odds_map[row["team"]] = row["win_probability"] or 0.0

    trends_rank = rank_by_value([(t, trends_map[t]) for t in TEAM_NAMES])
    mentions_rank = rank_by_value([(t, mentions_map[t]) for t in TEAM_NAMES])
    odds_rank = rank_by_value([(t, odds_map[t]) for t in TEAM_NAMES])

    interest_rank = {}
    for t in TEAM_NAMES:
        interest_rank[t] = round((trends_rank[t] + mentions_rank[t]) / 2, 2)

    composite_sorted = sorted(TEAM_NAMES, key=lambda t: interest_rank[t])
    interest_rank_int = {t: i + 1 for i, t in enumerate(composite_sorted)}

    rows = []
    for t in TEAM_NAMES:
        gap = interest_rank_int[t] - odds_rank[t]
        rows.append({
            "team": t,
            "odds_rank": odds_rank[t],
            "interest_rank": interest_rank_int[t],
            "trends_rank": trends_rank[t],
            "mentions_rank": mentions_rank[t],
            "win_probability": round(odds_map[t], 2),
            "trends_score": trends_map[t],
            "mentions": mentions_map[t],
            "gap": gap,
        })

    convergence = [
        r for r in rows
        if r["odds_rank"] <= CONVERGENCE_TOP_N
        and r["interest_rank"] <= CONVERGENCE_TOP_N
        and abs(r["gap"]) <= CONVERGENCE_MAX_GAP
    ]
    convergence.sort(key=lambda r: (r["odds_rank"] + r["interest_rank"]) / 2)
    convergence_teams = {r["team"] for r in convergence}

    underrated_by_fans = [
        r for r in rows
        if r["team"] not in convergence_teams
        and r["odds_rank"] < r["interest_rank"]
        and (r["interest_rank"] - r["odds_rank"]) >= DIVERGENCE_MIN_GAP
    ]
    underrated_by_fans.sort(key=lambda r: -(r["interest_rank"] - r["odds_rank"]))

    overrated_by_fans = [
        r for r in rows
        if r["team"] not in convergence_teams
        and r["interest_rank"] < r["odds_rank"]
        and (r["odds_rank"] - r["interest_rank"]) >= DIVERGENCE_MIN_GAP
    ]
    overrated_by_fans.sort(key=lambda r: -(r["odds_rank"] - r["interest_rank"]))

    return {
        "convergence": convergence,
        "higher_odds_lower_interest": underrated_by_fans,
        "higher_interest_lower_odds": overrated_by_fans,
    }
