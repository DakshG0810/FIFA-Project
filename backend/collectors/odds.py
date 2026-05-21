"""
collectors/odds.py
------------------
Fetches World Cup win probabilities from The Odds API.
Free tier: 500 requests/month — so we cache for 1 hour.
Converts decimal odds to implied probability.
Normalises all 32 teams so probabilities sum to 100%.
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from database import get_connection, ph
from teams import TEAMS, TEAM_NAMES

load_dotenv(find_dotenv())

def _log(msg: str):
    """Print safely on Windows consoles that lack UTF-8 emoji support."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"

# Map Odds API team names to our team names
ODDS_NAME_MAP = {
    "Argentina":      "Argentina",
    "France":         "France",
    "England":        "England",
    "Brazil":         "Brazil",
    "Spain":          "Spain",
    "Germany":        "Germany",
    "Portugal":       "Portugal",
    "Netherlands":    "Netherlands",
    "United States":  "USA",
    "Mexico":         "Mexico",
    "Canada":         "Canada",
    "Morocco":        "Morocco",
    "Senegal":        "Senegal",
    "Japan":          "Japan",
    "South Korea":    "South Korea",
    "Australia":      "Australia",
    "Iran":           "Iran",
    "Saudi Arabia":   "Saudi Arabia",
    "Ecuador":        "Ecuador",
    "Uruguay":        "Uruguay",
    "Colombia":       "Colombia",
    "Switzerland":    "Switzerland",
    "Croatia":        "Croatia",
    "Serbia":         "Serbia",
    "Poland":         "Poland",
    "Turkey":         "Turkey",
    "Nigeria":        "Nigeria",
    "Cameroon":       "Cameroon",
    "Venezuela":      "Venezuela",
    "Chile":          "Chile",
    "Peru":           "Peru",
    "New Zealand":    "New Zealand",
}

def collect_odds():
    _log(f"\n[Odds] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        _log("[Odds] No ODDS_API_KEY found in .env — skipping")
        return

    try:
        resp = requests.get(
            ODDS_API_URL,
            params={
                "apiKey": api_key,
                "regions": "uk,us,eu",
                "markets": "h2h",
                "oddsFormat": "decimal",
            },
            timeout=15,
        )
        resp.raise_for_status()
        # Log remaining API quota
        remaining = resp.headers.get("x-requests-remaining", "unknown")
        _log(f"  API requests remaining this month: {remaining}")
        data = resp.json()
    except Exception as e:
        _log(f"[Odds] API error: {e}")
        return

    # Aggregate odds per WC team only (ignore Draw, qualifiers, etc.)
    team_odds = {}
    for event in data:
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] != "h2h":
                    continue
                for outcome in market.get("outcomes", []):
                    raw_name = outcome["name"]
                    our_name = ODDS_NAME_MAP.get(raw_name)
                    if not our_name or our_name not in TEAM_NAMES:
                        continue
                    decimal = float(outcome["price"])
                    if decimal > 1:
                        prob = 1 / decimal
                        team_odds.setdefault(our_name, []).append({
                            "prob": prob,
                            "decimal": decimal,
                            "bookmaker": bookmaker["key"],
                        })

    if not team_odds:
        _log("[Odds] No odds data returned — World Cup odds may not be live yet")
        return

    # Average probability per team across bookmakers
    avg_probs = {}
    for team, entries in team_odds.items():
        avg_probs[team] = {
            "prob": sum(e["prob"] for e in entries) / len(entries),
            "decimal": sum(e["decimal"] for e in entries) / len(entries),
            "bookmaker": entries[0]["bookmaker"],
        }

    # Normalise across our 32 teams only
    total = sum(v["prob"] for v in avg_probs.values())
    if total > 0:
        for team in avg_probs:
            avg_probs[team]["prob_normalised"] = avg_probs[team]["prob"] / total

    conn = get_connection()
    cursor = conn.cursor()
    captured_at = datetime.now().isoformat()
    p = ph()
    saved = 0

    for team, data_ in avg_probs.items():
        cursor.execute(f"""
            INSERT INTO odds_snapshots
            (captured_at, team, win_probability, decimal_odds, bookmaker)
            VALUES ({p},{p},{p},{p},{p})
        """, (
            captured_at, team,
            round(data_.get("prob_normalised", data_["prob"]), 6),
            round(data_["decimal"], 2),
            data_["bookmaker"],
        ))
        saved += 1
        pct = round(data_.get("prob_normalised", data_["prob"]) * 100, 1)
        flag = TEAMS.get(team, {}).get("flag", "")
        _log(f"  {flag} {team}: {pct}%")

    conn.commit()
    conn.close()
    _log(f"[Odds] Done — {saved}/{len(TEAM_NAMES)} WC teams saved")

if __name__ == "__main__":
    collect_odds()
