"""
collectors/google_trends.py
----------------------------
Fetches Google Trends interest scores for all 48 WC teams.
Also stores football-only buzz keywords for the Trends word cloud:
  - team names weighted by search interest (0–100)
  - related rising/top queries when Google returns them
  - FIFA World Cup suggestion phrases
Batches teams into groups of 5 (API limit).
Waits 15 seconds between batches to avoid rate limiting.
"""
import sys
import os
import re
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pytrends.request import TrendReq
from database import get_connection, ph
from geo_regions import geos_for_today
from teams import TEAMS, get_trend_batches
from topics import is_football_keyword, CURATED_TRENDS_BUZZ

SUGGESTION_SEEDS = [
    "FIFA World Cup 2026",
    "World Cup 2026",
    "World Cup qualification",
    "World Cup group stage",
    "World Cup final",
]

PHRASE_PATTERNS = [
    "world cup", "fifa world cup", "qualification", "group stage", "knockout",
    "semifinal", "quarterfinal", "final", "golden boot", "penalty shootout",
    "opening match", "host nation", "world cup squad", "world cup draw",
]


def _parse_related_value(raw) -> int:
    if raw is None:
        return 25
    s = str(raw).strip().replace("%", "")
    if s.startswith("+"):
        s = s[1:]
    try:
        return max(5, min(100, int(float(s))))
    except ValueError:
        return 25


def _phrases_from_title(title: str) -> list[str]:
    t = title.lower()
    found = []
    for phrase in PHRASE_PATTERNS:
        if phrase in t and is_football_keyword(phrase):
            found.append(phrase)
    for token in re.findall(r"[a-z]{4,}", t):
        if is_football_keyword(token):
            found.append(token)
    return found


def _save_trends_keyword(cursor, captured_at, keyword, frequency, team_assoc, p):
    kw = keyword.lower().strip()
    if not is_football_keyword(kw):
        return
    cursor.execute(
        f"""
        INSERT INTO keyword_snapshots
        (captured_at, keyword, frequency, team_association, source)
        VALUES ({p},{p},{p},{p},{p})
        """,
        (captured_at, kw, frequency, team_assoc, "google_trends"),
    )


def _collect_suggestion_keywords(pt, cursor, captured_at, p):
    seen: set[str] = set()
    for seed in SUGGESTION_SEEDS:
        try:
            for item in pt.suggestions(keyword=seed) or []:
                title = (item.get("title") or "").strip()
                for phrase in _phrases_from_title(title):
                    if phrase in seen:
                        continue
                    seen.add(phrase)
                    _save_trends_keyword(cursor, captured_at, phrase, 40, None, p)
            time.sleep(2)
        except Exception as e:
            print(f"  Suggestions error ({seed}): {e}")


def _collect_related_keywords(pt, queries, team_batch, cursor, captured_at, p):
    try:
        related = pt.related_queries()
    except Exception:
        return
    if not related:
        return
    for j, team in enumerate(team_batch):
        query = queries[j]
        block = related.get(query)
        if not block:
            continue
        for kind in ("top", "rising"):
            df = block.get(kind)
            if df is None or df.empty:
                continue
            for _, row in df.iterrows():
                kw = str(row.get("query", "")).lower().strip()
                freq = _parse_related_value(row.get("value"))
                if kind == "rising":
                    freq = min(100, freq + 10)
                _save_trends_keyword(cursor, captured_at, kw, freq, team, p)


def _save_curated_category_buzz(cursor, captured_at, avg_interest: float, p):
    """Seed category filters (Players, Events, etc.) with football WC search terms."""
    base = max(avg_interest, 20)
    for kw, _category, weight in CURATED_TRENDS_BUZZ:
        freq = max(12, min(88, int(base * weight)))
        _save_trends_keyword(cursor, captured_at, kw, freq, None, p)


def _collect_regional_trends(pt, cursor, captured_at, p, batches):
    """Rotate 20 countries per run (~4 days to cover all map geos)."""
    geos = geos_for_today()
    regional_saved = 0
    print(f"  [Trends] Regional geos today: {', '.join(geos)}")

    for geo in geos:
        for i, batch in enumerate(batches):
            try:
                queries = [TEAMS[team]["trends_query"] for team in batch]
                pt.build_payload(
                    queries,
                    cat=20,
                    timeframe="now 7-d",
                    geo=geo,
                )
                df = pt.interest_over_time()
                if df.empty:
                    time.sleep(12)
                    continue

                for j, team in enumerate(batch):
                    query = queries[j]
                    if query not in df.columns:
                        continue
                    latest = int(df[query].iloc[-1])
                    cursor.execute(
                        f"""
                        INSERT INTO trends_snapshots (captured_at, team, interest_score, region)
                        VALUES ({p},{p},{p},{p})
                        """,
                        (captured_at, team, latest, geo),
                    )
                    regional_saved += 1

                if i < len(batches) - 1:
                    time.sleep(15)
            except Exception as e:
                print(f"  Regional {geo} batch {i + 1} error: {e}")
                time.sleep(20)

    return regional_saved


def collect_google_trends():
    print(f"\n[Trends] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    pt = TrendReq(hl='en-US', tz=0, timeout=(10, 30))
    conn = get_connection()
    cursor = conn.cursor()
    captured_at = datetime.now().isoformat()
    p = ph()
    total_saved = 0
    interest_scores: list[int] = []
    batches = get_trend_batches()

    _collect_suggestion_keywords(pt, cursor, captured_at, p)

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

                cursor.execute(f"""
                    INSERT INTO trends_snapshots (captured_at, team, interest_score, region)
                    VALUES ({p},{p},{p},{p})
                """, (captured_at, team, latest, "worldwide"))

                cursor.execute(f"""
                    INSERT INTO sentiment_snapshots
                    (captured_at, team, source, positive, negative, neutral, compound, mention_count)
                    VALUES ({p},{p},{p},{p},{p},{p},{p},{p})
                """, (
                    captured_at, team, "google_trends",
                    round(latest / 100, 4),
                    0,
                    round(1 - latest / 100, 4),
                    round((latest - 50) / 50, 4),
                    latest,
                ))

                _save_trends_keyword(cursor, captured_at, team.lower(), max(latest, 5), team, p)
                interest_scores.append(latest)
                total_saved += 1
                print(f"  {TEAMS[team]['flag']} {team}: {latest}/100")

            _collect_related_keywords(pt, queries, batch, cursor, captured_at, p)
            conn.commit()

            if i < len(batches) - 1:
                print(f"  Waiting 15s before next batch...")
                time.sleep(15)

        except Exception as e:
            print(f"  Batch {i+1} error: {e}")
            print(f"  Waiting 30s...")
            time.sleep(30)
            continue

    regional_saved = _collect_regional_trends(pt, cursor, captured_at, p, batches)
    conn.commit()

    conn.close()
    print(f"[Trends] Done — {total_saved} worldwide scores, {regional_saved} regional, buzz updated")


if __name__ == "__main__":
    collect_google_trends()
