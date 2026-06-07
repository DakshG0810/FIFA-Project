"""
One-time regional Google Trends backfill for all heatmap countries.

Collects per-country search interest for all 48 WC teams (geo != worldwide).
Run manually when you need the map populated immediately instead of waiting
for the daily 20-country rotation (~4 days).

  python -c "from collectors.regional_trends_backfill import backfill_regional_trends; backfill_regional_trends()"

Optional env:
  REGIONAL_GEOS=IN,US,GB   — only these ISO codes (for a quicker test run)
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
from geo_regions import COUNTRY_NAMES, all_map_geos
from teams import TEAMS, get_trend_batches

load_dotenv(find_dotenv())

BATCH_SLEEP_SEC = int(os.getenv("REGIONAL_BATCH_SLEEP", "15"))
GEO_SLEEP_SEC = int(os.getenv("REGIONAL_GEO_SLEEP", "20"))
MIN_GEOS_OK = int(os.getenv("REGIONAL_MIN_GEOS", "40"))


def _parse_geo_filter() -> list[str] | None:
    raw = (os.getenv("REGIONAL_GEOS") or "").strip()
    if not raw:
        return None
    return [g.strip().upper() for g in raw.split(",") if g.strip()]


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


def backfill_regional_trends():
    if USE_POSTGRES and not (os.getenv("DATABASE_URL") or "").strip():
        raise RuntimeError("DATABASE_URL is not set")

    geo_filter = _parse_geo_filter()
    geos = geo_filter if geo_filter else all_map_geos()
    batches = get_trend_batches()
    captured_at = datetime.now().isoformat()

    print(f"\n[Regional backfill] {len(geos)} countries × {len(batches)} team batches", flush=True)
    print(f"  Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}", flush=True)
    if geo_filter:
        print(f"  Filter: {', '.join(geos)}", flush=True)

    pt = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
    conn = get_connection()
    cursor = conn.cursor()
    p = ph()
    saved = 0
    geos_ok = 0
    errors: list[str] = []

    for g_idx, geo in enumerate(geos):
        label = COUNTRY_NAMES.get(geo, geo)
        geo_saved = 0
        print(f"\n  Geo {g_idx + 1}/{len(geos)}: {geo} ({label})", flush=True)

        for i, batch in enumerate(batches):
            queries = [TEAMS[team]["trends_query"] for team in batch]
            batch_saved = 0
            try:
                pt.build_payload(queries, cat=20, timeframe="now 7-d", geo=geo)
                df = pt.interest_over_time()
                if df.empty:
                    msg = f"{geo} batch {i + 1}: no data"
                    print(f"    {msg}", flush=True)
                    errors.append(msg)
                    time.sleep(12)
                    continue

                for j, team in enumerate(batch):
                    query = queries[j]
                    if query not in df.columns:
                        continue
                    value = _safe_int(df[query].iloc[-1])
                    _insert_trend(cursor, p, captured_at, team, value, geo)
                    saved += 1
                    batch_saved += 1
                    geo_saved += 1

                conn.commit()
                if batch_saved:
                    print(f"    Batch {i + 1}/{len(batches)} — {batch_saved} scores", flush=True)

                if i < len(batches) - 1:
                    time.sleep(BATCH_SLEEP_SEC)
            except Exception as e:
                safe_rollback(conn)
                msg = f"{geo} batch {i + 1} error: {e}"
                print(f"    {msg}", flush=True)
                errors.append(msg)
                time.sleep(30)

        if geo_saved > 0:
            geos_ok += 1
            print(f"    Done — {geo_saved} scores saved for {geo}", flush=True)
        else:
            print(f"    Skipped — no scores for {geo}", flush=True)

        if g_idx < len(geos) - 1:
            time.sleep(GEO_SLEEP_SEC)

    conn.close()
    print(
        f"\n[Regional backfill] Finished — {saved} rows, {geos_ok}/{len(geos)} countries with data",
        flush=True,
    )

    if geos_ok < MIN_GEOS_OK and not geo_filter:
        for err in errors[:8]:
            print(f"  - {err}", flush=True)
        raise RuntimeError(
            f"Only {geos_ok}/{len(geos)} countries succeeded (need {MIN_GEOS_OK})"
        )


if __name__ == "__main__":
    try:
        backfill_regional_trends()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
