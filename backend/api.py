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
                       AVG(positive)  as positive,
                       AVG(negative)  as negative,
                       AVG(compound)  as compound,
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
                       AVG(positive)  as positive,
                       AVG(negative)  as negative,
                       AVG(compound)  as compound,
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
    placeholders = ",".join([p] * len(TEAM_NAMES))
    rows = conn.execute(f"""
        SELECT DISTINCT ON (team) team, win_probability, decimal_odds, bookmaker, captured_at
        FROM odds_snapshots
        WHERE team IN ({placeholders})
        ORDER BY team, captured_at DESC
    """, tuple(TEAM_NAMES)).fetchall()
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

    if source:
        rows = conn.execute(f"""
            SELECT keyword, SUM(frequency) as total_freq, MAX(team_association) as team_association
            FROM keyword_snapshots
            WHERE source = {p} {time_clause}
            GROUP BY keyword
            ORDER BY total_freq DESC
            LIMIT {p}
        """, (source, *time_params, limit * 3)).fetchall()
    else:
        rows = conn.execute(f"""
            SELECT keyword, SUM(frequency) as total_freq, MAX(team_association) as team_association
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

    sentiment = conn.execute(f"""
        SELECT team,
               AVG(compound) as compound,
               AVG(positive) as positive,
               AVG(negative) as negative,
               SUM(mention_count) as mentions,
               SUM(reach_score) as reach
        FROM sentiment_snapshots
        WHERE source = {p}
        GROUP BY team
    """, ("bluesky",)).fetchall()

    odds = conn.execute("""
        SELECT team, win_probability
        FROM odds_snapshots
        WHERE captured_at = (SELECT MAX(captured_at) FROM odds_snapshots)
    """).fetchall()

    trends = conn.execute("""
        SELECT team, interest_score
        FROM trends_snapshots
        WHERE captured_at = (SELECT MAX(captured_at) FROM trends_snapshots)
    """).fetchall()

    momentum_rows = conn.execute(f"""
        SELECT team, compound, captured_at FROM sentiment_snapshots
        WHERE source = {p}
        ORDER BY captured_at ASC
    """, ("bluesky",)).fetchall()

    conn.close()

    odds_map   = {r["team"]: r["win_probability"] for r in odds if r["team"] in TEAM_NAMES}
    trends_map = {r["team"]: r["interest_score"]  for r in trends}

    momentum_map = {}
    by_team = {}
    for row in momentum_rows:
        by_team.setdefault(row["team"], []).append(row["compound"] or 0)
    for team, values in by_team.items():
        if len(values) < 2:
            momentum_map[team] = "flat"
        else:
            delta = values[-1] - values[0]
            if delta > 0.05:
                momentum_map[team] = "up"
            elif delta < -0.05:
                momentum_map[team] = "down"
            else:
                momentum_map[team] = "flat"

    sentiment_map = {row["team"]: row for row in sentiment if row["team"] in TEAM_NAMES}
    result = []
    for team in TEAM_NAMES:
        row = sentiment_map.get(team)
        result.append({
            "team":            team,
            "compound":        round((row["compound"] if row else 0) or 0, 4),
            "positive":        round((row["positive"] if row else 0) or 0, 4),
            "negative":        round((row["negative"] if row else 0) or 0, 4),
            "mentions":        (row["mentions"] if row else 0) or 0,
            "reach":           (row["reach"] if row else 0) or 0,
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
