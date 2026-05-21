"""
Test Bluesky credentials without running a full collection.

Usage (from backend/ folder):
  python test_bluesky_auth.py
"""
import os
import sys

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from collectors.bluesky import (
    credentials_configured,
    get_access_token,
    search_posts,
    demo_fallback_enabled,
)


def main():
    print("=" * 50)
    print("PulseCup — Bluesky connection test")
    print("=" * 50)

    handle = os.getenv("BLUESKY_HANDLE", "").strip()
    has_pw = bool(os.getenv("BLUESKY_APP_PASSWORD", "").strip())
    demo = demo_fallback_enabled()

    print(f"BLUESKY_HANDLE set:        {'yes' if handle else 'NO'}")
    if handle:
        print(f"  handle: {handle}")
    print(f"BLUESKY_APP_PASSWORD set:  {'yes' if has_pw else 'NO'}")
    print(f"BLUESKY_DEMO_FALLBACK:     {demo}")

    if not credentials_configured():
        print("\nResult: NOT CONFIGURED")
        print("Add BLUESKY_HANDLE and BLUESKY_APP_PASSWORD to .env")
        print("See docs/BLUESKY_SETUP.md")
        sys.exit(1)

    print("\nTrying login...")
    token = get_access_token()
    if not token:
        print("Login: FAILED")
        print("Check handle (include .bsky.social) and app password (not your main password).")
        sys.exit(1)
    print("Login: OK")

    print("\nTrying search (World Cup 2026)...")
    posts, err = search_posts("World Cup 2026", limit=5)
    if posts:
        print(f"Search: OK ({len(posts)} posts returned)")
        sample = posts[0].get("record", {}).get("text", "")[:80]
        if sample:
            print(f"  Sample: {sample}...")
    else:
        print(f"Search: FAILED ({err})")
        sys.exit(1)

    print("\nAll checks passed. Run: python -c \"from collectors.bluesky import collect_bluesky; collect_bluesky()\"")
    sys.exit(0)


if __name__ == "__main__":
    main()
