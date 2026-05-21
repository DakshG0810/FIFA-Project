"""
database.py
-----------
Handles all database connections and table creation.
Works with SQLite locally and PostgreSQL on Render (production).
SQLite = development on your laptop.
PostgreSQL = deployed on Render, data persists forever.
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
USE_POSTGRES = bool(DATABASE_URL)


class _QueryResult:
    """Wraps a DB cursor so conn.execute(...).fetchall() works everywhere."""

    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class DbConnection:
    """
    SQLite (3.12+) and psycopg2 both support conn.execute in our API layer.
    PostgreSQL raw connections do not — this adapter adds execute().
    """

    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=None):
        cur = self._conn.cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return _QueryResult(cur)

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_connection():
    if USE_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        kwargs = {"cursor_factory": RealDictCursor}
        if "sslmode=" not in DATABASE_URL:
            kwargs["sslmode"] = "require"
        raw = psycopg2.connect(DATABASE_URL, **kwargs)
        return DbConnection(raw)
    else:
        conn = sqlite3.connect("wc_dashboard.db")
        conn.row_factory = sqlite3.Row
        return conn

def placeholder(n=1):
    """
    Returns the right SQL placeholder.
    SQLite uses ? — PostgreSQL uses %s
    """
    if USE_POSTGRES:
        return ",".join(["%s"] * n)
    return ",".join(["?"] * n)

def ph():
    """Single placeholder shorthand."""
    return "%s" if USE_POSTGRES else "?"

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # sentiment_snapshots
    # Stores per-team sentiment from Bluesky + Google Trends interest scores
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS sentiment_snapshots (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            captured_at TEXT NOT NULL,
            team TEXT NOT NULL,
            source TEXT NOT NULL,
            positive REAL DEFAULT 0,
            negative REAL DEFAULT 0,
            neutral REAL DEFAULT 0,
            compound REAL DEFAULT 0,
            mention_count INTEGER DEFAULT 0,
            reach_score REAL DEFAULT 0
        )
    """)

    # odds_snapshots
    # Stores win probability per team over time
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS odds_snapshots (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            captured_at TEXT NOT NULL,
            team TEXT NOT NULL,
            win_probability REAL,
            decimal_odds REAL,
            bookmaker TEXT
        )
    """)

    # keyword_snapshots
    # Top keywords extracted from Bluesky posts
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS keyword_snapshots (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            captured_at TEXT NOT NULL,
            keyword TEXT NOT NULL,
            frequency INTEGER DEFAULT 0,
            team_association TEXT
        )
    """)

    # trends_snapshots
    # Google Trends interest score per team per region
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS trends_snapshots (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            captured_at TEXT NOT NULL,
            team TEXT NOT NULL,
            interest_score INTEGER DEFAULT 0,
            region TEXT DEFAULT 'worldwide'
        )
    """)

    # viral_spikes
    # Detected spikes in mention volume
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS viral_spikes (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            detected_at TEXT NOT NULL,
            team TEXT NOT NULL,
            source TEXT NOT NULL,
            mentions_current INTEGER,
            mentions_average REAL,
            spike_multiplier REAL,
            inferred_trigger TEXT
        )
    """)

    # influencer_snapshots — top Bluesky accounts by reach
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS influencer_snapshots (
            id {'SERIAL' if USE_POSTGRES else 'INTEGER'} PRIMARY KEY {'AUTOINCREMENT' if not USE_POSTGRES else ''},
            captured_at TEXT NOT NULL,
            handle TEXT NOT NULL,
            display_name TEXT,
            reach_score REAL DEFAULT 0,
            primary_team TEXT,
            sentiment REAL DEFAULT 0,
            viral_post TEXT
        )
    """)

    # Indexes for fast time-series queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_team_time ON sentiment_snapshots(team, captured_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_team_time ON odds_snapshots(team, captured_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trends_team_time ON trends_snapshots(team, captured_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_influencer_time ON influencer_snapshots(captured_at)")

    conn.commit()
    conn.close()
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    print(f"[DB] Initialised ({db_type})")

if __name__ == "__main__":
    init_db()
