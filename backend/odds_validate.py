"""
Sanity checks for bookmaker outright winner odds.
Guards against normalised/partial API responses that inflate longshots (e.g. DR Congo ~20%).
"""

from teams import TEAM_NAMES

MIN_TEAMS = 40
MIN_TOTAL_PROB = 1.15
MAX_TOTAL_PROB = 3.5
MAX_TOP_PROB = 0.22

# Teams that should never lead a 48-nation WC winner market
IMPLAUSIBLE_FAVOURITES = frozenset({
    "DR Congo", "Cabo Verde", "Haiti", "Jordan", "Iraq", "Uzbekistan",
    "Curaçao", "Panama", "New Zealand", "Bosnia and Herzegovina",
    "Czechia", "Scotland", "Norway", "Sweden", "Switzerland",
})

# Any of these should realistically top the market when data is valid
PLAUSIBLE_FAVOURITES = frozenset({
    "Argentina", "Brazil", "France", "England", "Spain", "Germany",
    "Portugal", "Netherlands", "Belgium", "Croatia", "USA", "Mexico",
    "Colombia", "Uruguay", "Italy", "Morocco", "Japan",
})


def snapshot_stats(rows) -> dict | None:
    """Build stats from rows with team + win_probability (+ optional decimal_odds)."""
    pairs = []
    for r in rows:
        team = r["team"] if isinstance(r, dict) else r[0]
        prob = r["win_probability"] if isinstance(r, dict) else r[1]
        if team not in TEAM_NAMES or prob is None:
            continue
        pairs.append((team, float(prob)))
    if not pairs:
        return None
    pairs.sort(key=lambda x: -x[1])
    top_team, top_prob = pairs[0]
    return {
        "team_count": len(pairs),
        "total_prob": sum(p for _, p in pairs),
        "top_team": top_team,
        "top_prob": top_prob,
    }


def validate_snapshot_stats(stats: dict | None) -> tuple[bool, str]:
    if not stats:
        return False, "empty snapshot"
    if stats["team_count"] < MIN_TEAMS:
        return False, f"only {stats['team_count']} teams (need {MIN_TEAMS})"
    total = stats["total_prob"]
    if total <= 1.05:
        return False, f"normalised probabilities (sum={total:.3f})"
    if total < MIN_TOTAL_PROB:
        return False, f"sum too low ({total:.3f}) — partial/inflated market"
    if total > MAX_TOTAL_PROB:
        return False, f"sum too high ({total:.3f})"
    top_team = stats["top_team"]
    top_prob = stats["top_prob"]
    if top_prob > MAX_TOP_PROB:
        return False, f"top probability {top_prob * 100:.1f}% too high"
    if top_team in IMPLAUSIBLE_FAVOURITES and top_prob > 0.03:
        return False, f"implausible favourite {top_team} at {top_prob * 100:.1f}%"
    if top_team not in PLAUSIBLE_FAVOURITES and top_prob > 0.12:
        return False, f"unexpected favourite {top_team} at {top_prob * 100:.1f}%"
    return True, "ok"


def validate_prob_map(prob_map: dict[str, float]) -> tuple[bool, str]:
    rows = [{"team": t, "win_probability": p} for t, p in prob_map.items()]
    return validate_snapshot_stats(snapshot_stats(rows))


def purge_invalid_odds_snapshots(conn) -> int:
    """Delete entire captured_at groups that fail sanity checks."""
    from database import ph

    p = ph()
    captures = conn.execute(
        "SELECT captured_at FROM odds_snapshots GROUP BY captured_at ORDER BY captured_at DESC"
    ).fetchall()
    removed = 0
    for cap_row in captures:
        cap = cap_row["captured_at"]
        rows = conn.execute(
            f"SELECT team, win_probability FROM odds_snapshots WHERE captured_at = {p}",
            (cap,),
        ).fetchall()
        ok, _reason = validate_snapshot_stats(snapshot_stats(rows))
        if not ok:
            conn.execute(
                f"DELETE FROM odds_snapshots WHERE captured_at = {p}",
                (cap,),
            )
            removed += 1
    if removed:
        conn.commit()
    return removed


def pick_bookmaker_favourite(odds_map: dict[str, float]) -> dict | None:
    """Best defensible favourite from a team → probability map (mirrors frontend logic)."""
    eligible = []
    for team, prob in odds_map.items():
        if prob is None or prob <= 0 or prob > MAX_TOP_PROB:
            continue
        if team in IMPLAUSIBLE_FAVOURITES and prob > 0.03:
            continue
        eligible.append((team, float(prob)))
    if not eligible:
        return None
    team, prob = max(eligible, key=lambda x: x[1])
    return {"team": team, "win_probability": prob}


def latest_valid_capture(conn) -> str | None:
    """Return captured_at of the newest odds snapshot that passes all checks."""
    from database import ph

    p = ph()
    captures = conn.execute(
        "SELECT captured_at FROM odds_snapshots GROUP BY captured_at ORDER BY captured_at DESC"
    ).fetchall()
    for cap_row in captures:
        cap = cap_row["captured_at"]
        rows = conn.execute(
            f"SELECT team, win_probability FROM odds_snapshots WHERE captured_at = {p}",
            (cap,),
        ).fetchall()
        ok, _reason = validate_snapshot_stats(snapshot_stats(rows))
        if ok:
            return cap
    return None
