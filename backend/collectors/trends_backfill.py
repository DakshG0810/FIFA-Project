"""
One-time Google Trends backfill from project start date (2026-05-21).

Fetches daily worldwide interest scores for all 48 WC teams so every nation
shares the same historical scale before normal daily collection continues.

Run once via GitHub Actions (workflow_dispatch) or locally:
  python -c "from collectors.trends_backfill import backfill_worldwide_trends; backfill_worldwide_trends()"
"""

import math
import os
import sys
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from pytrends.request import TrendReq

from database import get_connection, ph, safe_rollback, USE_POSTGRES
from teams import TEAMS, get_trend_batches

load_dotenv(find_dotenv())

BACKFILL_START = os.getenv("TRENDS_BACKFILL_START", "2026-05-21")
MIN_BATCHES_OK = int(os.getenv("TRENDS_BACKFILL_MIN_BATCHES", "8"))


def _day_exists(conn, team: str, day: str, p) -> bool:
    """Use conn.execute — required for PostgreSQL (cursor.execute returns None)."""
    row = conn.execute(
        f"""
        SELECT 1 FROM trends_snapshots
        WHERE team = {p} AND region = 'worldwide' AND substr(captured_at, 1, 10) = {p}
        LIMIT 1
        """,
        (team, day),
    ).fetchone()
    return row is not None


def _insert_trend(cursor, p, captured_at: str, team: str, value: int, region: str):
    cursor.execute(
        f"""
        INSERT INTO trends_snapshots (captured_at, team, interest_score, region)
        VALUES ({p},{p},{p},{p})
        """,
        (captured_at, team, value, region),
    )


def _safe_int(value) -> int:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def backfill_worldwide_trends():
    if USE_POSTGRES and not (os.getenv("DATABASE_URL") or "").strip():
        raise RuntimeError("DATABASE_URL is not set — add it to GitHub Actions secrets")

    end = datetime.now().strftime("%Y-%m-%d")
    timeframe = f"{BACKFILL_START} {end}"
    print(f"\n[Trends backfill] {timeframe} — worldwide daily scores", flush=True)
    print(f"  Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}", flush=True)

    pt = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    batches = get_trend_batches()
    saved = 0
    skipped = 0
    batches_ok = 0
    errors: list[str] = []

    for i, batch in enumerate(batches):
        queries = [TEAMS[team]["trends_query"] for team in batch]
        batch_saved = 0
        try:
            pt.build_payload(queries, cat=20, timeframe=timeframe, geo="")
            df = pt.interest_over_time()
            if df.empty:
                msg = f"Batch {i + 1}/{len(batches)}: no data returned"
                print(f"  {msg}", flush=True)
                errors.append(msg)
                time.sleep(15)
                continue

            for date_idx, _row in df.iterrows():
                day = date_idx.strftime("%Y-%m-%d")
                captured_at = f"{day}T12:00:00"
                for j, team in enumerate(batch):
                    query = queries[j]
                    if query not in df.columns:
                        continue
                    value = _safe_int(df[query].loc[date_idx])
                    if _day_exists(conn, team, day, p):
                        skipped += 1
                        continue
                    _insert_trend(cursor, p, captured_at, team, value, "worldwide")
                    saved += 1
                    batch_saved += 1

            conn.commit()
            batches_ok += 1
            print(
                f"  Batch {i + 1}/{len(batches)} done — {batch_saved} new rows this batch",
                flush=True,
            )
            if i < len(batches) - 1:
                time.sleep(15)
        except Exception as e:
            safe_rollback(conn)
            msg = f"Batch {i + 1} error: {e}"
            print(f"  {msg}", flush=True)
            errors.append(msg)
            time.sleep(30)

    conn.close()
    print(
        f"[Trends backfill] Done — {saved} new rows, {skipped} already present, "
        f"{batches_ok}/{len(batches)} batches OK",
        flush=True,
    )

    if batches_ok < MIN_BATCHES_OK:
        print("[Trends backfill] FAILED — too few batches succeeded", flush=True)
        for err in errors[:5]:
            print(f"  - {err}", flush=True)
        raise RuntimeError(
            f"Only {batches_ok}/{len(batches)} batches succeeded (need {MIN_BATCHES_OK})"
        )


if __name__ == "__main__":
    try:
        backfill_worldwide_trends()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
