"""
Roll up Bluesky sentiment: one snapshot per team per calendar day (latest run),
then sum daily post counts for totals. Avoids double-counting reruns on the same day.
"""

from collections import defaultdict

from teams import TEAM_NAMES


def _rollup_rows(rows) -> dict[str, dict]:
    latest_per_day: dict[tuple[str, str], object] = {}
    for row in rows:
        team = row["team"]
        day = row["captured_at"][:10]
        key = (team, day)
        prev = latest_per_day.get(key)
        if not prev or row["captured_at"] > prev["captured_at"]:
            latest_per_day[key] = row

    totals: dict[str, dict] = defaultdict(
        lambda: {
            "mentions": 0,
            "reach": 0,
            "compound_w": 0.0,
            "positive_w": 0.0,
            "negative_w": 0.0,
            "weight": 0,
            "daily_compounds": [],
        }
    )

    for (team, day), row in latest_per_day.items():
        if team not in TEAM_NAMES:
            continue
        mc = row["mention_count"] or 0
        bucket = totals[team]
        bucket["mentions"] += mc
        bucket["reach"] += row["reach_score"] or 0
        bucket["compound_w"] += (row["compound"] or 0) * mc
        bucket["positive_w"] += (row["positive"] or 0) * mc
        bucket["negative_w"] += (row["negative"] or 0) * mc
        bucket["weight"] += mc
        bucket["daily_compounds"].append((day, row["compound"] or 0))

    result = {}
    for team in TEAM_NAMES:
        bucket = totals[team]
        w = bucket["weight"]
        daily = sorted(bucket["daily_compounds"])
        result[team] = {
            "mentions": bucket["mentions"],
            "reach": bucket["reach"],
            "compound": round(bucket["compound_w"] / w, 4) if w else 0.0,
            "positive": round(bucket["positive_w"] / w, 4) if w else 0.0,
            "negative": round(bucket["negative_w"] / w, 4) if w else 0.0,
            "daily_compounds": daily,
        }
    return result


def bluesky_team_totals_from_conn(conn) -> dict[str, dict]:
    from database import ph

    p = ph()
    rows = conn.execute(
        f"""
        SELECT team, captured_at, mention_count, compound, positive, negative, reach_score
        FROM sentiment_snapshots
        WHERE source = {p}
        ORDER BY team, captured_at
        """,
        ("bluesky",),
    ).fetchall()
    return _rollup_rows(rows)
