"""
scheduler.py
------------
Runs all three collectors on a schedule.
Google Trends: every 6 hours (rate limit friendly)
Bluesky:       every 30 minutes
Odds:          every 60 minutes (saves free API quota)

Run this once and leave it running in a terminal.
It will collect data around the clock automatically.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from database import init_db
from collectors.bluesky import collect_bluesky
from collectors.google_trends import collect_google_trends
from collectors.odds import collect_odds

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

def run_all_once():
    print(f"\n{'='*52}")
    print(f"[Scheduler] First run — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*52}")
    run_bluesky()
    run_trends()
    run_odds()

if __name__ == "__main__":
    init_db()
    run_all_once()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_bluesky, "interval", minutes=30,  id="bluesky")
    scheduler.add_job(run_trends,  "interval", hours=6,     id="trends")
    scheduler.add_job(run_odds,    "interval", minutes=60,  id="odds")

    print("\n[Scheduler] Running. Schedule:")
    print("  Bluesky      — every 30 minutes")
    print("  Google Trends — every 6 hours")
    print("  Odds API     — every 60 minutes")
    print("  Press Ctrl+C to stop\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Scheduler] Stopped.")
