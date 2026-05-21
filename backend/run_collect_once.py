"""
One-shot collection for GitHub Actions or manual runs.
Does not start a long-running scheduler.
"""

from database import init_db
from scheduler import run_all_collectors

if __name__ == "__main__":
    init_db()
    run_all_collectors()
