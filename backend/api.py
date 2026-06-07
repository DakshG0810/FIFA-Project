"""
api.py
------
FastAPI server that serves all collected data to the frontend.
Run with: python api.py
Then open: http://localhost:8000/docs for interactive API docs.

Endpoints:
  GET /api/status              — health check, last collection times
  GET /api/sentiment           — latest sentiment per team (all sources)
  GET /api/sentiment/{team}    — sentiment history for one team
  GET /api/odds                — latest win probabilities
  GET /api/odds/{team}/history — odds movement over time
  GET /api/trends              — latest Google Trends scores
  GET /api/keywords            — top keywords right now
  GET /api/leaderboard         — combined ranked leaderboard
  GET /api/spikes              — detected viral spikes
"""

import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection, init_db, ph
from teams import TEAM_NAMES, TEAMS, CONFEDERATION_COLORS
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from api_analytics import router as analytics_router
from odds_validate import latest_valid_capture, pick_bookmaker_favourite, purge_invalid_odds_snapshots

load_dotenv(find_dotenv())

DATA_STALE_HOURS = float(os.getenv("DATA_STALE_HOURS", "30"))
COLLECT_INTERVAL_HOURS = int(os.getenv("COLLECT_INTERVAL_HOURS", "24"))

_cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
_frontend = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
if _frontend:
    _cors_origins.append(_frontend)

app = FastAPI(
    title="WC Dashboard API",
    description="FIFA World Cup 2026 fan sentiment analytics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(analytics_router)

@app.on_event("startup")
def startup():
    try:
        init_db()
        conn = get_connection()
        n = purge_invalid_odds_snapshots(conn)
        conn.close()
        if n:
            print(f"[Odds] Purged {n} invalid snapshot(s) on startup")
    except Exception as e:
        print(f"[DB] Startup init warning: {e}")

# ── Helpers ──────────────────────────────────────────────────────────────────

def since(hours=24):
    return (datetime.now() - timedelta(hours=hours)).isoformat()

def rows_to_list(rows):
    return [dict(r) for r in rows]

def fill_sentiment_rows(rows, source: str | None = None):
    """Ensure all 48 WC teams appear, with zeros when no data yet."""
    data = {r["team"]: r for r in rows if r["team"] in TEAM_NAMES}
    result = []
    for team in TEAM_NAMES:
        r = data.get(team)
        entry = {
            "team": team,
            "positive": round((r["positive"] if r else 0) or 0, 4),
            "negative": round((r["negative"] if r else 0) or 0, 4),
            "compound": round((r["compound"] if r else 0) or 0, 4),
            "mentions": (r["mentions"] if r else 0) or 0,
            "total_reach": (r["total_reach"] if r else 0) or 0,
        }
        if source:
            entry["source"] = (r["source"] if r else source)
        result.append(entry)
    result.sort(key=lambda x: x["mentions"], reverse=True)
    return result

def source_mode(last_iso: str | None, stale_hours: float | None = None) -> str:
    if stale_hours is None:
        stale_hours = DATA_STALE_HOURS
    """LIVE = fresh collection, CACHED = stale, empty = no data."""
    if not last_iso:
        return "empty"
    try:
        ts = datetime.fromisoformat(last_iso.replace("Z", "").split("+")[0])
        age_h = (datetime.now() - ts).total_seconds() / 3600
        return "live" if age_h <= stale_hours else "cached"
    except ValueError:
        return "cached"

def bluesky_status_label(last_iso: str | None) -> str:
    """Badge label for /api/status — demo only when using synthetic fallback."""
    import os
    has_creds = bool(os.getenv("BLUESKY_HANDLE", "").strip() and os.getenv("BLUESKY_APP_PASSWORD", "").strip())
    demo_on = os.getenv("BLUESKY_DEMO_FALLBACK", "true").lower() in ("1", "true", "yes")
    if has_creds:
        return source_mode(last_iso, stale_hours=DATA_STALE_HOURS) if last_iso else "empty"
    if demo_on and last_iso:
        return "demo"
    return source_mode(last_iso) if last_iso else "empty"

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/team/{team}/inspect")
def inspect_team(team: str):
    """Manual sanity check — raw Bluesky sentiment + odds for one team."""
    if team not in TEAM_NAMES:
        return {"error": f"Unknown team: {team}"}
    conn = get_connection()
    p = ph()
    latest_odds = latest_valid_capture(conn)
    odds_row = None
    if latest_odds:
        odds_row = conn.execute(
            f"""
            SELECT win_probability, decimal_odds, bookmaker, captured_at
            FROM odds_snapshots WHERE team = {p} AND captured_at = {p}
            """,
            (team, latest_odds),
        ).fetchone()
    bluesky = conn.execute(
        f"""
        SELECT SUM(mention_count) as mentions,
               SUM(compound * mention_count) / NULLIF(SUM(mention_count), 0) as compound,
               COUNT(*) as collection_runs,
               MAX(captured_at) as last_capture
        FROM sentiment_snapshots WHERE team = {p} AND source = {p}
        """,
        (team, "bluesky"),
    ).fetchone()
    conn.close()
    wp = (odds_row["win_probability"] if odds_row else None)
    return {
        "team": team,
        "odds": {
            "win_probability": wp,
            "win_percent": round(wp * 100, 2) if wp else None,
            "decimal_odds": odds_row["decimal_odds"] if odds_row else None,
            "bookmaker": odds_row["bookmaker"] if odds_row else None,
            "captured_at": odds_row["captured_at"] if odds_row else None,
            "snapshot_valid": latest_odds is not None,
        },
        "bluesky": {
            "mentions": bluesky["mentions"] if bluesky else 0,
            "compound_weighted": round((bluesky["compound"] if bluesky else 0) or 0, 4),
            "collection_runs": bluesky["collection_runs"] if bluesky else 0,
            "last_capture": bluesky["last_capture"] if bluesky else None,
        },
    }


@app.get("/api/status")
def status():
    conn = get_connection()
    p = ph()
    last_bluesky = conn.execute(
        f"SELECT MAX(captured_at) as t FROM sentiment_snapshots WHERE source={p}",
        ("bluesky",)
    ).fetchone()
    last_trends = conn.execute(
        f"SELECT MAX(captured_at) as t FROM trends_snapshots"
    ).fetchone()
    last_odds = conn.execute(
        f"SELECT MAX(captured_at) as t FROM odds_snapshots"
    ).fetchone()
    valid_odds_cap = latest_valid_capture(conn)
    bookmaker_fav = None
    if valid_odds_cap:
        odds_rows = conn.execute(
            f"SELECT team, win_probability FROM odds_snapshots WHERE captured_at = {p}",
            (valid_odds_cap,),
        ).fetchall()
        bookmaker_fav = pick_bookmaker_favourite(
            {r["team"]: r["win_probability"] for r in odds_rows}
        )
    total = conn.execute(
        "SELECT COUNT(*) as n FROM sentiment_snapshots"
    ).fetchone()
    conn.close()
    lb = last_bluesky["t"] if last_bluesky else None
    lt = last_trends["t"]  if last_trends  else None
    lo = last_odds["t"]    if last_odds    else None
    has_bsky_creds = bool(os.getenv("BLUESKY_HANDLE", "").strip() and os.getenv("BLUESKY_APP_PASSWORD", "").strip())
    return {
        "status": "ok",
        "last_bluesky":       lb,
        "last_google_trends": lt,
        "last_odds":          lo,
        "last_valid_odds":    valid_odds_cap,
        "bookmaker_favourite": bookmaker_fav,
        "total_snapshots":    total["n"]        if total        else 0,
        "server_time":        datetime.now().isoformat(),
        "bluesky_configured": has_bsky_creds,
        "bluesky_demo_fallback": os.getenv("BLUESKY_DEMO_FALLBACK", "true").lower() in ("1", "true", "yes"),
        "data_sources": {
            "bluesky":       bluesky_status_label(lb),
            "google_trends": source_mode(lt),
            "odds":          source_mode(lo),
        },
        "collection_schedule": {
            "interval_hours": COLLECT_INTERVAL_HOURS,
            "note": "Bluesky, Google Trends, and Odds run together on this interval",
        },
    }

@app.get("/api/sentiment")
def get_sentiment(
    hours: int = Query(24, description="Hours to look back; 0 = all time"),
    source: str = Query(None, description="Filter by source: bluesky or google_trends"),
):
    """Latest combined sentiment per team."""
    conn = get_connection()
    p = ph()
    if source:
        if hours <= 0:
            rows = conn.execute(f"""
                SELECT team,
                       SUM(positive * mention_count) / NULLIF(SUM(mention_count), 0) as positive,
                       SUM(negative * mention_count) / NULLIF(SUM(mention_count), 0) as negative,
                       SUM(compound * mention_count) / NULLIF(SUM(mention_count), 0) as compound,
                       SUM(mention_count) as mentions,
                       SUM(reach_score)   as total_reach,
                       MAX(source) as source
                FROM sentiment_snapshots
                WHERE source = {p}
                GROUP BY team
                ORDER BY mentions DESC
            """, (source,)).fetchall()
        else:
            rows = conn.execute(f"""
                SELECT team,
                       SUM(positive * mention_count) / NULLIF(SUM(mention_count), 0) as positive,
                       SUM(negative * mention_count) / NULLIF(SUM(mention_count), 0) as negative,
                       SUM(compound * mention_count) / NULLIF(SUM(mention_count), 0) as compound,
                       SUM(mention_count) as mentions,
                       SUM(reach_score)   as total_reach,
                       MAX(source) as source
                FROM sentiment_snapshots
                WHERE captured_at > {p} AND source = {p}
                GROUP BY team
                ORDER BY mentions DESC
            """, (since(hours), source)).fetchall()
    else:
        time_clause = "" if hours <= 0 else f"WHERE captured_at > {p}"
        params = () if hours <= 0 else (since(hours),)
        rows = conn.execute(f"""
            SELECT team,
                   AVG(positive)  as positive,
                   AVG(negative)  as negative,
                   AVG(compound)  as compound,
                   SUM(mention_count) as mentions,
                   SUM(reach_score)   as total_reach
            FROM sentiment_snapshots
            {time_clause}
            GROUP BY team
            ORDER BY mentions DESC
        """, params).fetchall()
    conn.close()
    return fill_sentiment_rows(rows, source)

@app.get("/api/teams")
def get_teams():
    """All 48 World Cup 2026 teams with confederation metadata."""
    return [
        {
            "team": name,
            "confederation": TEAMS[name]["confederation"],
            "confederation_color": CONFEDERATION_COLORS.get(TEAMS[name]["confederation"], "#888780"),
        }
        for name in TEAM_NAMES
    ]

@app.get("/api/sentiment/{team}/history")
def get_team_sentiment_history(
    team: str,
    days: int = Query(365),
    source: str = Query("bluesky", description="bluesky or google_trends"),
):
    """Sentiment time series — one point per collection day."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(f"""
        SELECT substr(captured_at, 1, 10) as captured_at,
               AVG(compound)  as compound,
               SUM(mention_count) as mentions
        FROM sentiment_snapshots
        WHERE team = {p} AND source = {p} AND captured_at > {p}
        GROUP BY substr(captured_at, 1, 10)
        ORDER BY substr(captured_at, 1, 10) ASC
    """, (team, source, since(days * 24))).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/odds")
def get_odds():
    """Latest win probability per team — all 48 WC nations."""
    conn = get_connection()
    p = ph()
    latest = latest_valid_capture(conn)
    placeholders = ",".join([p] * len(TEAM_NAMES))
    if latest:
        rows = conn.execute(f"""
            SELECT team, win_probability, decimal_odds, bookmaker, captured_at
            FROM odds_snapshots
            WHERE team IN ({placeholders}) AND captured_at = {p}
        """, (*TEAM_NAMES, latest)).fetchall()
    else:
        rows = []
    conn.close()
    data = {r["team"]: r for r in rows}
    result = []
    for team in TEAM_NAMES:
        r = data.get(team)
        result.append({
            "team": team,
            "win_probability": (r["win_probability"] if r else None),
            "decimal_odds": (r["decimal_odds"] if r else None),
            "bookmaker": (r["bookmaker"] if r else None),
            "captured_at": (r["captured_at"] if r else None),
        })
    result.sort(key=lambda x: x["win_probability"] or 0, reverse=True)
    return result

@app.get("/api/odds/{team}/history")
def get_odds_history(team: str, days: int = Query(30)):
    """Odds movement over time for one team."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(f"""
        SELECT captured_at, win_probability, decimal_odds
        FROM odds_snapshots
        WHERE team = {p} AND captured_at > {p}
        ORDER BY captured_at ASC
    """, (team, since(days * 24))).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/trends")
def get_trends():
    """Latest Google Trends interest score per team."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT ON (team) team, interest_score, region, captured_at
        FROM trends_snapshots
        WHERE region = 'worldwide'
        ORDER BY team, captured_at DESC
    """).fetchall()
    conn.close()
    data = {r["team"]: r for r in rows if r["team"] in TEAM_NAMES}
    result = []
    for team in TEAM_NAMES:
        r = data.get(team)
        result.append({
            "team": team,
            "interest_score": (r["interest_score"] if r else 0) or 0,
            "region": (r["region"] if r else "worldwide"),
            "captured_at": r["captured_at"] if r else None,
        })
    result.sort(key=lambda x: x["interest_score"], reverse=True)
    return result

@app.get("/api/keywords")
def get_keywords(
    hours: int = Query(168, description="Hours to look back; 0 = all time"),
    limit: int = Query(80),
    category: str = Query(None, description="all|players|events|emotions|tactical"),
    source: str = Query(None, description="bluesky or google_trends"),
):
    """Top buzz keywords — Bluesky post terms or Google Trends search buzz."""
    from topics import keyword_category, is_football_keyword

    conn = get_connection()
    p = ph()
    time_clause = "" if hours <= 0 else f"AND captured_at > {p}"
    time_params: tuple = () if hours <= 0 else (since(hours),)

    # MAX not SUM — avoids flat duplicate frequencies stacking to equal word sizes
    if source:
        rows = conn.execute(f"""
            SELECT keyword, MAX(frequency) as total_freq, MAX(team_association) as team_association
            FROM keyword_snapshots
            WHERE source = {p} {time_clause}
            GROUP BY keyword
            ORDER BY total_freq DESC
            LIMIT {p}
        """, (source, *time_params, limit * 3)).fetchall()
    else:
        rows = conn.execute(f"""
            SELECT keyword, MAX(frequency) as total_freq, MAX(team_association) as team_association
            FROM keyword_snapshots
            WHERE 1=1 {time_clause}
            GROUP BY keyword
            ORDER BY total_freq DESC
            LIMIT {p}
        """, (*time_params, limit * 3)).fetchall()
    conn.close()

    result = [r for r in rows_to_list(rows) if is_football_keyword(r["keyword"])]
    if category and category != "all":
        result = [r for r in result if keyword_category(r["keyword"]) == category]
    return result[:limit]

@app.get("/api/leaderboard")
def get_leaderboard():
    """
    Combined leaderboard merging sentiment, odds, and trends.
    This is the main endpoint for the dashboard overview.
    """
    conn = get_connection()
    p = ph()

    from sentiment_aggregate import bluesky_team_totals_from_conn

    bluesky_totals = bluesky_team_totals_from_conn(conn)

    latest_odds = latest_valid_capture(conn)
    if latest_odds:
        odds = conn.execute(f"""
            SELECT team, win_probability
            FROM odds_snapshots
            WHERE captured_at = {p}
        """, (latest_odds,)).fetchall()
    else:
        odds = []

    trends = conn.execute("""
        SELECT team, interest_score
        FROM trends_snapshots
        WHERE region = 'worldwide'
        AND captured_at = (
            SELECT MAX(captured_at) FROM trends_snapshots WHERE region = 'worldwide'
        )
    """).fetchall()

    conn.close()

    odds_map   = {r["team"]: r["win_probability"] for r in odds if r["team"] in TEAM_NAMES}
    trends_map = {r["team"]: r["interest_score"]  for r in trends}

    momentum_map = {}
    for team, totals in bluesky_totals.items():
        daily = totals["daily_compounds"]
        if len(daily) < 2:
            momentum_map[team] = "flat"
        else:
            delta = daily[-1][1] - daily[0][1]
            if delta > 0.05:
                momentum_map[team] = "up"
            elif delta < -0.05:
                momentum_map[team] = "down"
            else:
                momentum_map[team] = "flat"

    result = []
    for team in TEAM_NAMES:
        row = bluesky_totals.get(team)
        result.append({
            "team":            team,
            "compound":        row["compound"] if row else 0,
            "positive":        row["positive"] if row else 0,
            "negative":        row["negative"] if row else 0,
            "mentions":        row["mentions"] if row else 0,
            "reach":           row["reach"] if row else 0,
            "win_probability": odds_map.get(team),
            "trends_score":    trends_map.get(team),
            "momentum":        momentum_map.get(team, "flat"),
        })

    result.sort(key=lambda x: x["mentions"], reverse=True)
    return result

@app.get("/api/spikes")
def get_spikes(hours: int = Query(24)):
    """Viral spikes detected in the last N hours."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(f"""
        SELECT * FROM viral_spikes
        WHERE detected_at > {p}
        ORDER BY detected_at DESC
        LIMIT 20
    """, (since(hours),)).fetchall()
    conn.close()
    return rows_to_list(rows)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
