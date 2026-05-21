"""
collectors/bluesky.py
---------------------
Fetches posts from Bluesky (public or authenticated API).
Runs VADER sentiment, extracts keywords, detects viral spikes.
Falls back to deterministic demo posts when the public API returns 403.
"""

import hashlib
import os
import re
import time
import requests
from datetime import datetime, timedelta
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv, find_dotenv
from database import get_connection, ph
from teams import TEAMS
from topics import assign_cluster

load_dotenv(find_dotenv())

analyzer = SentimentIntensityAnalyzer()

PUBLIC_SEARCH = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
AUTH_SEARCH = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
SESSION_URL = "https://bsky.social/xrpc/com.atproto.server.createSession"

_access_token = None

STOPWORDS = {
    "this", "that", "with", "have", "from", "they", "will", "been",
    "were", "their", "what", "when", "about", "which", "would", "could",
    "should", "there", "these", "those", "them", "then", "than", "your",
    "just", "like", "more", "some", "also", "into", "over", "after",
    "world", "soccer", "football", "team", "game", "play", "match",
    "player", "sport", "ball", "goal", "score", "season", "league",
    "bluesky", "bsky", "post", "thread", "reply", "https", "http",
    "think", "know", "really", "good", "great", "best", "people",
    "2026", "fifa", "worldcup", "world", "cup",
}

DEMO_TEMPLATES = [
    "{team} are looking brilliant heading into World Cup 2026",
    "VAR decision went against {team} — fans furious",
    "{team} injury doubt before the tournament opener",
    "That goal for {team} was absolutely world class",
    "{team} tactics and pressing looked elite tonight",
    "{team} got robbed, should have been a penalty",
    "Is {team} overrated or genuinely elite? debate continues",
    "{team} squad announcement drops — huge reactions",
    "Messi level performance from {team} tonight",
    "{team} bottled it in the second half honestly",
]


def _log(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def demo_fallback_enabled():
    val = os.getenv("BLUESKY_DEMO_FALLBACK", "")
    if val:
        return val.lower() in ("1", "true", "yes")
    return os.getenv("ENV", "development") == "development"


def credentials_configured() -> bool:
    return bool(os.getenv("BLUESKY_HANDLE", "").strip() and os.getenv("BLUESKY_APP_PASSWORD", "").strip())


def get_access_token():
    """Optional authenticated session (recommended when public search returns 403)."""
    global _access_token
    if _access_token:
        return _access_token

    handle = os.getenv("BLUESKY_HANDLE", "").strip()
    password = os.getenv("BLUESKY_APP_PASSWORD", "").strip()
    if not handle or not password:
        return None

    try:
        resp = requests.post(
            SESSION_URL,
            json={"identifier": handle, "password": password},
            timeout=15,
        )
        resp.raise_for_status()
        _access_token = resp.json().get("accessJwt")
        if _access_token:
            _log("[Bluesky] Authenticated session created")
        return _access_token
    except Exception as e:
        body = ""
        if hasattr(e, "response") and e.response is not None:
            try:
                body = e.response.text[:200]
            except Exception:
                pass
        _log(f"[Bluesky] Auth failed: {e}")
        if body:
            _log(f"  Detail: {body}")
        _log("  Tip: use an App Password from bsky.app/settings/app-passwords (not your login password)")
        return None


def _team_seed(team_name: str) -> int:
    return int(hashlib.md5(team_name.encode()).hexdigest()[:8], 16)


def generate_demo_posts(team_name: str, count: int) -> list[dict]:
    """Deterministic synthetic posts when live API is unavailable."""
    seed = _team_seed(team_name)
    posts = []
    for i in range(count):
        tpl = DEMO_TEMPLATES[(seed + i) % len(DEMO_TEMPLATES)]
        text = tpl.format(team=team_name)
        compound = analyzer.polarity_scores(text)["compound"]
        posts.append({
            "text": text,
            "likes": 5 + (seed + i * 7) % 120,
            "reposts": 1 + (seed + i * 3) % 40,
            "replies": (seed + i) % 15,
            "handle": f"fan{(seed + i) % 99}.bsky.social",
            "display_name": f"{team_name} Fan",
            "created_at": datetime.now().isoformat(),
            "_compound_hint": compound,
        })
    return posts


def search_posts(query: str, limit: int = 50) -> tuple[list, str | None]:
    """
    Try authenticated bsky.social first, then public AppView.
    Returns (posts, error_reason).
    """
    token = get_access_token()
    attempts = []
    if token:
        attempts.append((AUTH_SEARCH, {"Authorization": f"Bearer {token}"}))
    attempts.append((PUBLIC_SEARCH, {}))

    last_error = None
    for url, headers in attempts:
        try:
            resp = requests.get(
                url,
                params={"q": query, "limit": limit},
                headers=headers,
                timeout=12,
            )
            if resp.status_code == 200:
                return resp.json().get("posts", []), None
            last_error = f"{resp.status_code} {resp.reason}"
        except Exception as e:
            last_error = str(e)
        time.sleep(0.4)

    return [], last_error


def fetch_team_posts(team_name, team_data, limit=50):
    """Fetch Bluesky posts for a team; returns list of parsed post dicts."""
    all_posts = []
    seen_uris = set()
    queries = [
        f"{team_name} WorldCup2026",
        f"{team_name} FIFA2026",
    ]
    api_failed = False

    for query in queries:
        raw, err = search_posts(query, limit=limit)
        if err and not raw:
            api_failed = True
            if err.startswith("403"):
                continue
        for post in raw:
            uri = post.get("uri", "")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                all_posts.append(parse_post(post))
            elif not uri:
                all_posts.append(parse_post(post))
        time.sleep(0.5)

    if not all_posts and api_failed:
        if credentials_configured() and not demo_fallback_enabled():
            _log(f"  [Bluesky] No live posts for {team_name} (search unavailable)")
            return []
        if demo_fallback_enabled():
            seed = _team_seed(team_name)
            count = 18 + (seed % 25)
            _log(f"  [Bluesky] Demo fallback for {team_name} ({count} posts)")
            return generate_demo_posts(team_name, count)

    return all_posts


def parse_post(post):
    record = post.get("record", {})
    author = post.get("author", {})
    return {
        "text": record.get("text", post.get("text", "")),
        "likes": post.get("likeCount", 0),
        "reposts": post.get("repostCount", 0),
        "replies": post.get("replyCount", 0),
        "handle": author.get("handle", ""),
        "display_name": author.get("displayName", ""),
        "created_at": record.get("createdAt", ""),
    }


def detect_viral_spike(cursor, team_name, current_mentions, captured_at, p):
    """Flag when current mentions exceed 3x the 6-hour rolling average."""
    six_hours_ago = (datetime.now() - timedelta(hours=6)).isoformat()
    cursor.execute(
        f"""
        SELECT AVG(mention_count) as avg_mentions
        FROM sentiment_snapshots
        WHERE team = {p} AND source = {p}
          AND captured_at > {p} AND captured_at < {p}
        """,
        (team_name, "bluesky", six_hours_ago, captured_at),
    )
    row = cursor.fetchone()

    avg = row["avg_mentions"] if row else None
    if not avg or avg <= 0:
        return

    if current_mentions <= 3 * avg:
        return

    multiplier = round(current_mentions / avg, 2)
    pct_increase = round((multiplier - 1) * 100)
    trigger = f"Mentions up {pct_increase}% vs 6hr average — fan discussion surge"

    cursor.execute(
        f"""
        INSERT INTO viral_spikes
        (detected_at, team, source, mentions_current, mentions_average,
         spike_multiplier, inferred_trigger)
        VALUES ({p},{p},{p},{p},{p},{p},{p})
        """,
        (
            captured_at, team_name, "bluesky",
            current_mentions, round(avg, 2), multiplier, trigger,
        ),
    )


def save_team_snapshot(cursor, captured_at, team_name, parsed, p):
    texts = [p_["text"] for p_ in parsed if p_.get("text")]
    if not texts:
        return 0, []

    scores = [analyzer.polarity_scores(t) for t in texts]
    n = len(scores)
    avg_pos = sum(s["pos"] for s in scores) / n
    avg_neg = sum(s["neg"] for s in scores) / n
    avg_neu = sum(s["neu"] for s in scores) / n
    avg_comp = sum(s["compound"] for s in scores) / n
    total_reach = sum(p_["likes"] + p_["reposts"] for p_ in parsed)

    cursor.execute(
        f"""
        INSERT INTO sentiment_snapshots
        (captured_at, team, source, positive, negative, neutral, compound, mention_count, reach_score)
        VALUES ({p},{p},{p},{p},{p},{p},{p},{p},{p})
        """,
        (
            captured_at, team_name, "bluesky",
            round(avg_pos, 4), round(avg_neg, 4),
            round(avg_neu, 4), round(avg_comp, 4),
            n, total_reach,
        ),
    )

    keywords = []
    for text in texts:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        keywords.extend((w, team_name) for w in words if w not in STOPWORDS)

    detect_viral_spike(cursor, team_name, n, captured_at, p)
    return n, keywords, parsed


def track_influencers(influencer_agg, team_name, parsed):
    for post in parsed:
        handle = post.get("handle")
        if not handle:
            continue
        reach = post["likes"] + post["reposts"]
        if handle not in influencer_agg:
            influencer_agg[handle] = {
                "handle": handle,
                "display_name": post.get("display_name") or handle,
                "reach": 0,
                "teams": [],
                "posts": [],
                "sentiment_sum": 0.0,
                "count": 0,
            }
        influencer_agg[handle]["reach"] += reach
        influencer_agg[handle]["teams"].append(team_name)
        influencer_agg[handle]["posts"].append(post)
        if post.get("text"):
            influencer_agg[handle]["sentiment_sum"] += analyzer.polarity_scores(post["text"])["compound"]
        influencer_agg[handle]["count"] += 1


def save_influencers(cursor, captured_at, influencer_agg, p):
    cursor.execute("DELETE FROM influencer_snapshots")
    ranked = sorted(influencer_agg.values(), key=lambda x: x["reach"], reverse=True)[:20]
    for inf in ranked:
        primary = Counter(inf["teams"]).most_common(1)[0][0] if inf["teams"] else None
        sentiment = inf["sentiment_sum"] / max(inf["count"], 1)
        viral = max(inf["posts"], key=lambda x: x["likes"] + x["reposts"])
        viral_text = (viral.get("text") or "")[:280]
        cursor.execute(
            f"""
            INSERT INTO influencer_snapshots
            (captured_at, handle, display_name, reach_score, primary_team, sentiment, viral_post)
            VALUES ({p},{p},{p},{p},{p},{p},{p})
            """,
            (
                captured_at, inf["handle"], inf["display_name"],
                inf["reach"], primary, round(sentiment, 4), viral_text,
            ),
        )


def collect_bluesky():
    _log(f"\n[Bluesky] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    token = get_access_token()
    if credentials_configured() and not token:
        _log("[Bluesky] ABORT: Credentials in .env but login failed.")
        _log("  Fix BLUESKY_HANDLE / BLUESKY_APP_PASSWORD — see docs/BLUESKY_SETUP.md")
        return
    if token:
        _log("[Bluesky] Mode: LIVE (authenticated search)")
    elif demo_fallback_enabled():
        _log("[Bluesky] Mode: DEMO fallback enabled (no credentials or public API only)")
    else:
        _log("[Bluesky] Mode: LIVE required — set credentials or enable BLUESKY_DEMO_FALLBACK")

    conn = get_connection()
    cursor = conn.cursor()
    captured_at = datetime.now().isoformat()
    p = ph()

    teams_with_data = 0
    all_keywords = []
    used_demo = False
    influencer_agg = {}

    for team_name, team_data in TEAMS.items():
        parsed = fetch_team_posts(team_name, team_data)
        if not parsed:
            continue

        if any("_compound_hint" in post for post in parsed):
            used_demo = True
            parsed = [{k: v for k, v in post.items() if k != "_compound_hint"} for post in parsed]

        n, keywords, parsed = save_team_snapshot(cursor, captured_at, team_name, parsed, p)
        if n == 0:
            continue

        track_influencers(influencer_agg, team_name, parsed)
        all_keywords.extend(keywords)
        teams_with_data += 1
        avg_comp = analyzer.polarity_scores(parsed[0]["text"])["compound"] if parsed else 0
        total_reach = sum(p_["likes"] + p_["reposts"] for p_ in parsed)
        _log(f"  {team_data['flag']} {team_name}: {n} posts, reach={total_reach}")

    word_counts = Counter(w for w, _ in all_keywords).most_common(50)
    for keyword, freq in word_counts:
        team_words = [t for w, t in all_keywords if w == keyword]
        top_team = Counter(team_words).most_common(1)
        team_assoc = top_team[0][0] if top_team else None
        cursor.execute(
            f"""
            INSERT INTO keyword_snapshots (captured_at, keyword, frequency, team_association)
            VALUES ({p},{p},{p},{p})
            """,
            (captured_at, keyword, freq, team_assoc),
        )

    if influencer_agg:
        save_influencers(cursor, captured_at, influencer_agg, p)

    conn.commit()
    conn.close()

    mode = "DEMO" if used_demo else "LIVE"
    _log(f"[Bluesky] Done ({mode}) — {teams_with_data} teams, {len(word_counts)} keywords")


if __name__ == "__main__":
    collect_bluesky()
