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
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="WC Dashboard API",
    description="FIFA World Cup 2026 fan sentiment analytics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# ── Helpers ──────────────────────────────────────────────────────────────────

def since(hours=24):
    return (datetime.now() - timedelta(hours=hours)).isoformat()

def rows_to_list(rows):
    return [dict(r) for r in rows]

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
    return {
        "status": "ok",
        "last_bluesky":       last_bluesky["t"] if last_bluesky else None,
        "last_google_trends": last_trends["t"]  if last_trends  else None,
        "last_odds":          last_odds["t"]    if last_odds    else None,
        "total_snapshots":    total["n"]        if total        else 0,
        "server_time":        datetime.now().isoformat(),
    }

@app.get("/api/sentiment")
def get_sentiment(
    hours: int = Query(24, description="Hours to look back"),
    source: str = Query(None, description="Filter by source: bluesky or google_trends"),
):
    """Latest combined sentiment per team."""
    conn = get_connection()
    p = ph()
    if source:
        rows = conn.execute(f"""
            SELECT team,
                   AVG(positive)  as positive,
                   AVG(negative)  as negative,
                   AVG(compound)  as compound,
                   SUM(mention_count) as mentions,
                   SUM(reach_score)   as total_reach,
                   source
            FROM sentiment_snapshots
            WHERE captured_at > {p} AND source = {p}
            GROUP BY team
            ORDER BY mentions DESC
        """, (since(hours), source)).fetchall()
    else:
        rows = conn.execute(f"""
            SELECT team,
                   AVG(positive)  as positive,
                   AVG(negative)  as negative,
                   AVG(compound)  as compound,
                   SUM(mention_count) as mentions,
                   SUM(reach_score)   as total_reach
            FROM sentiment_snapshots
            WHERE captured_at > {p}
            GROUP BY team
            ORDER BY mentions DESC
        """, (since(hours),)).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/sentiment/{team}/history")
def get_team_sentiment_history(team: str, days: int = Query(30)):
    """Sentiment time series for one team."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(f"""
        SELECT captured_at, source,
               AVG(compound)  as compound,
               SUM(mention_count) as mentions
        FROM sentiment_snapshots
        WHERE team = {p} AND captured_at > {p}
        GROUP BY substr(captured_at, 1, 13), source
        ORDER BY captured_at ASC
    """, (team, since(days * 24))).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/odds")
def get_odds():
    """Latest win probability per team."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT team, win_probability, decimal_odds, bookmaker,
               MAX(captured_at) as captured_at
        FROM odds_snapshots
        GROUP BY team
        ORDER BY win_probability DESC
    """).fetchall()
    conn.close()
    return rows_to_list(rows)

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
        SELECT team, interest_score, region, MAX(captured_at) as captured_at
        FROM trends_snapshots
        GROUP BY team
        ORDER BY interest_score DESC
    """).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/keywords")
def get_keywords(hours: int = Query(24), limit: int = Query(30)):
    """Top keywords in the last N hours."""
    conn = get_connection()
    p = ph()
    rows = conn.execute(f"""
        SELECT keyword, SUM(frequency) as total_freq, team_association
        FROM keyword_snapshots
        WHERE captured_at > {p}
        GROUP BY keyword
        ORDER BY total_freq DESC
        LIMIT {p}
    """, (since(hours), limit)).fetchall()
    conn.close()
    return rows_to_list(rows)

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
        WHERE captured_at > {p} AND source = {p}
        GROUP BY team
    """, (since(48), "bluesky")).fetchall()

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

    conn.close()

    odds_map   = {r["team"]: r["win_probability"] for r in odds}
    trends_map = {r["team"]: r["interest_score"]  for r in trends}

    result = []
    for row in sentiment:
        team = row["team"]
        result.append({
            "team":            team,
            "compound":        round(row["compound"] or 0, 4),
            "positive":        round(row["positive"] or 0, 4),
            "negative":        round(row["negative"] or 0, 4),
            "mentions":        row["mentions"] or 0,
            "reach":           row["reach"] or 0,
            "win_probability": odds_map.get(team),
            "trends_score":    trends_map.get(team),
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
