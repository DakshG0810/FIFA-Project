"""
scheduler.py
------------
Runs all collectors on a schedule (default: once per day).

Set COLLECT_INTERVAL_HOURS=24 on Render to stay within free-tier limits.
"""

import os
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from database import init_db
from collectors.bluesky import collect_bluesky
from collectors.google_trends import collect_google_trends
from collectors.odds import collect_odds

load_dotenv(find_dotenv())

COLLECT_INTERVAL_HOURS = max(1, int(os.getenv("COLLECT_INTERVAL_HOURS", "24")))


def run_bluesky():
    try:
        collect_bluesky()
    except Exception as e:
        print(f"[Scheduler] Bluesky error: {e}")


def run_trends():
    try:
        collect_google_trends()
    except Exception as e:
        print(f"[Scheduler] Trends error: {e}")


def run_odds():
    try:
        collect_odds()
    except Exception as e:
        print(f"[Scheduler] Odds error: {e}")


def run_all_collectors():
    print(f"\n{'='*52}")
    print(f"[Scheduler] Collection run — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*52}")
    run_bluesky()
    run_trends()
    run_odds()
    print(f"[Scheduler] Run complete — next in {COLLECT_INTERVAL_HOURS}h\n")


if __name__ == "__main__":
    init_db()
    run_all_collectors()

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_all_collectors,
        "interval",
        hours=COLLECT_INTERVAL_HOURS,
        id="daily_collect",
    )

    print("[Scheduler] Running. Schedule:")
    print(f"  All sources (Bluesky + Trends + Odds) — every {COLLECT_INTERVAL_HOURS} hours")
    print("  Press Ctrl+C to stop\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Scheduler] Stopped.")
