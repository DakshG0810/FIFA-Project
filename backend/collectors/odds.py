"""
collectors/odds.py
------------------
Fetches World Cup winner probabilities from The Odds API.
Uses the soccer_fifa_world_cup_winner outrights market (all 48 nations).
Free tier: 500 requests/month — collected once per daily run.
"""

import os
import unicodedata
import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from database import get_connection, ph
from teams import TEAMS, TEAM_NAMES

load_dotenv(find_dotenv())

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup_winner/odds/"

# Map Odds API team names → our canonical team names
ODDS_NAME_MAP = {
    # AFC
    "Australia": "Australia",
    "Iran": "Iran",
    "Iraq": "Iraq",
    "Japan": "Japan",
    "Jordan": "Jordan",
    "Qatar": "Qatar",
    "Saudi Arabia": "Saudi Arabia",
    "South Korea": "South Korea",
    "Korea Republic": "South Korea",
    "Uzbekistan": "Uzbekistan",
    # CAF
    "Algeria": "Algeria",
    "Cabo Verde": "Cabo Verde",
    "Cape Verde": "Cabo Verde",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Egypt": "Egypt",
    "Ghana": "Ghana",
    "Ivory Coast": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Morocco": "Morocco",
    "Senegal": "Senegal",
    "South Africa": "South Africa",
    "Tunisia": "Tunisia",
    # CONCACAF
    "Canada": "Canada",
    "Curaçao": "Curaçao",
    "Curacao": "Curaçao",
    "Haiti": "Haiti",
    "Mexico": "Mexico",
    "Panama": "Panama",
    "United States": "USA",
    "USA": "USA",
    # CONMEBOL
    "Argentina": "Argentina",
    "Brazil": "Brazil",
    "Colombia": "Colombia",
    "Ecuador": "Ecuador",
    "Paraguay": "Paraguay",
    "Uruguay": "Uruguay",
    # OFC
    "New Zealand": "New Zealand",
    # UEFA
    "Austria": "Austria",
    "Belgium": "Belgium",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Croatia": "Croatia",
    "Czechia": "Czechia",
    "Czech Republic": "Czechia",
    "England": "England",
    "France": "France",
    "Germany": "Germany",
    "Netherlands": "Netherlands",
    "Norway": "Norway",
    "Portugal": "Portugal",
    "Scotland": "Scotland",
    "Spain": "Spain",
    "Sweden": "Sweden",
    "Switzerland": "Switzerland",
    "Turkey": "Turkey",
    "Türkiye": "Turkey",
}

# Pre-build normalised lookup for encoding mismatches (e.g. Curaçao → Curacao)
_NORMALISED_MAP: dict[str, str] = {}
for raw, canonical in ODDS_NAME_MAP.items():
    key = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii").lower()
    _NORMALISED_MAP[key] = canonical


def _log(msg: str):
    """Print safely on Windows consoles that lack UTF-8 emoji support."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def map_odds_team(raw_name: str) -> str | None:
    """Resolve an Odds API outcome name to our team name."""
    if raw_name in ("Draw",):
        return None
    if raw_name in ODDS_NAME_MAP:
        canonical = ODDS_NAME_MAP[raw_name]
        return canonical if canonical in TEAM_NAMES else None
    key = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode("ascii").lower()
    canonical = _NORMALISED_MAP.get(key)
    return canonical if canonical in TEAM_NAMES else None


def collect_odds():
    _log(f"\n[Odds] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    api_key = (os.getenv("ODDS_API_KEY") or "").strip()
    if not api_key:
        _log("[Odds] No ODDS_API_KEY found in .env — skipping")
        return

    try:
        resp = requests.get(
            ODDS_API_URL,
            params={
                "apiKey": api_key,
                "regions": "uk,us,eu",
                "markets": "outrights",
                "oddsFormat": "decimal",
            },
            timeout=15,
        )
        resp.raise_for_status()
        remaining = resp.headers.get("x-requests-remaining", "unknown")
        _log(f"  API requests remaining this month: {remaining}")
        data = resp.json()
    except Exception as e:
        _log(f"[Odds] API error: {e}")
        return

    # Outrights: one event, each bookmaker lists all nations with winner odds
    team_odds: dict[str, list] = {}
    unmapped: set[str] = set()
    for event in data:
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] != "outrights":
                    continue
                for outcome in market.get("outcomes", []):
                    raw_name = outcome["name"]
                    our_name = map_odds_team(raw_name)
                    if not our_name:
                        if raw_name not in ("Draw",):
                            unmapped.add(raw_name)
                        continue
                    decimal = float(outcome["price"])
                    if decimal > 1:
                        team_odds.setdefault(our_name, []).append({
                            "prob": 1 / decimal,
                            "decimal": decimal,
                            "bookmaker": bookmaker["key"],
                        })

    if unmapped:
        _log(f"  Ignored non-WC outcomes: {', '.join(sorted(unmapped))}")

    if not team_odds:
        _log("[Odds] No outright winner odds returned")
        return

    avg_probs = {}
    for team, entries in team_odds.items():
        avg_probs[team] = {
            "prob": sum(e["prob"] for e in entries) / len(entries),
            "decimal": sum(e["decimal"] for e in entries) / len(entries),
            "bookmaker": entries[0]["bookmaker"],
        }

    # Normalise so listed teams sum to 100% (bookmakers also price non-qualifiers)
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
    missing = [t for t in TEAM_NAMES if t not in avg_probs]
    if missing:
        _log(f"[Odds] Warning — no odds for: {', '.join(missing)}")
    _log(f"[Odds] Done — {saved}/{len(TEAM_NAMES)} WC teams saved")


if __name__ == "__main__":
    collect_odds()
