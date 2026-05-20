"""
collectors/google_trends.py
----------------------------
Fetches Google Trends interest scores for all 32 WC teams.
Batches teams into groups of 5 (API limit).
Waits 15 seconds between batches to avoid rate limiting.
Stores 0-100 interest score per team per region.
"""

import time
from datetime import datetime
from pytrends.request import TrendReq
from database import get_connection, ph
from teams import TEAMS, get_trend_batches

def collect_google_trends():
    print(f"\n[Trends] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    pt = TrendReq(hl='en-US', tz=0, timeout=(10, 30))
    conn = get_connection()
    cursor = conn.cursor()
    captured_at = datetime.now().isoformat()
    p = ph()
    total_saved = 0
    batches = get_trend_batches()

    for i, batch in enumerate(batches):
        try:
            queries = [TEAMS[team]["trends_query"] for team in batch]
            pt.build_payload(
                queries,
                cat=20,           # Sports category
                timeframe='now 7-d',
                geo='',           # Worldwide
            )
            df = pt.interest_over_time()

            if df.empty:
                print(f"  Batch {i+1}/{len(batches)}: no data returned")
                time.sleep(15)
                continue

            for j, team in enumerate(batch):
                query = queries[j]
                if query not in df.columns:
                    continue

                latest = int(df[query].iloc[-1])
                avg    = float(df[query].mean())

                cursor.execute(f"""
                    INSERT INTO trends_snapshots (captured_at, team, interest_score, region)
                    VALUES ({p},{p},{p},{p})
                """, (captured_at, team, latest, "worldwide"))

                # Also save as a sentiment snapshot so the API can serve it uniformly
                cursor.execute(f"""
                    INSERT INTO sentiment_snapshots
                    (captured_at, team, source, positive, negative, neutral, compound, mention_count)
                    VALUES ({p},{p},{p},{p},{p},{p},{p},{p})
                """, (
                    captured_at, team, "google_trends",
                    round(latest / 100, 4),   # positive proxy
                    0,
                    round(1 - latest / 100, 4),
                    round((latest - 50) / 50, 4),  # compound -1 to 1
                    latest,
                ))

                total_saved += 1
                print(f"  {TEAMS[team]['flag']} {team}: {latest}/100")

            conn.commit()

            if i < len(batches) - 1:
                print(f"  Waiting 15s before next batch...")
                time.sleep(15)

        except Exception as e:
            print(f"  Batch {i+1} error: {e}")
            print(f"  Waiting 30s...")
            time.sleep(30)
            continue

    conn.close()
    print(f"[Trends] Done — {total_saved} team scores saved")

if __name__ == "__main__":
    collect_google_trends()
