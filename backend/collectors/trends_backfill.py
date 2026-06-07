"""
One-time Google Trends backfill from project start date (2026-05-21).

Fetches daily worldwide interest scores for all 48 WC teams so every nation
shares the same historical scale before normal daily collection continues.

Run once via GitHub Actions (workflow_dispatch) or locally:
  python -m collectors.trends_backfill
"""

import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv, find_dotenv
from pytrends.request import TrendReq

from database import get_connection, ph
from teams import TEAMS, get_trend_batches

load_dotenv(find_dotenv())

BACKFILL_START = os.getenv("TRENDS_BACKFILL_START", "2026-05-21")


def _day_exists(cursor, team: str, day: str, p) -> bool:
    row = cursor.execute(
        f"""
        SELECT 1 FROM trends_snapshots
        WHERE team = {p} AND region = 'worldwide' AND substr(captured_at, 1, 10) = {p}
        LIMIT 1
        """,
        (team, day),
    ).fetchone()
    return row is not None


def backfill_worldwide_trends():
    end = datetime.now().strftime("%Y-%m-%d")
    timeframe = f"{BACKFILL_START} {end}"
    print(f"\n[Trends backfill] {timeframe} — worldwide daily scores")

    pt = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    batches = get_trend_batches()
    saved = 0
    skipped = 0

    for i, batch in enumerate(batches):
        queries = [TEAMS[team]["trends_query"] for team in batch]
        try:
            pt.build_payload(queries, cat=20, timeframe=timeframe, geo="")
            df = pt.interest_over_time()
            if df.empty:
                print(f"  Batch {i + 1}/{len(batches)}: no data")
                time.sleep(15)
                continue

            for date_idx, _row in df.iterrows():
                day = date_idx.strftime("%Y-%m-%d")
                captured_at = f"{day}T12:00:00"
                for j, team in enumerate(batch):
                    query = queries[j]
                    if query not in df.columns:
                        continue
                    value = int(df[query].loc[date_idx])
                    if _day_exists(cursor, team, day, p):
                        skipped += 1
                        continue
                    cursor.execute(
                        f"""
                        INSERT INTO trends_snapshots (captured_at, team, interest_score, region)
                        VALUES ({p},{p},{p},{p})
                        """,
                        (captured_at, team, value, "worldwide"),
                    )
                    saved += 1

            conn.commit()
            print(f"  Batch {i + 1}/{len(batches)} done")
            if i < len(batches) - 1:
                time.sleep(15)
        except Exception as e:
            print(f"  Batch {i + 1} error: {e}")
            time.sleep(30)

    conn.close()
    print(f"[Trends backfill] Done — {saved} new rows, {skipped} already present")


if __name__ == "__main__":
    backfill_worldwide_trends()
