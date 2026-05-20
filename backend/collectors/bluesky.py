"""
collectors/bluesky.py
---------------------
Fetches posts from Bluesky's fully public API.
No API key or login required.
Runs sentiment analysis using VADER on each post.
Extracts top keywords and detects viral spikes.
"""

import re
import time
import requests
from datetime import datetime
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import get_connection, ph
from teams import TEAMS

analyzer = SentimentIntensityAnalyzer()

BLUESKY_API = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"

# Words too generic to be useful as keywords
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

# Topic cluster keyword mapping
CLUSTERS = {
    "Injuries & fitness":    ["injured", "injury", "fitness", "doubt", "out", "strain", "surgery", "recovery", "unavailable"],
    "Goals & results":       ["goal", "scored", "winner", "equaliser", "result", "score", "final", "victory", "defeat", "draw"],
    "Referee & VAR":         ["var", "offside", "penalty", "referee", "decision", "overturned", "foul", "card", "red", "yellow"],
    "Tactics & lineup":      ["formation", "pressing", "substitution", "lineup", "tactics", "coach", "manager", "system", "squad"],
    "Fan banter":            ["overrated", "bottled", "class", "elite", "fraud", "goat", "terrible", "brilliant", "deserve"],
    "Squad & transfers":     ["squad", "called up", "dropped", "transfer", "contract", "captain", "selected", "roster"],
}

def assign_cluster(text):
    text_lower = text.lower()
    for cluster, keywords in CLUSTERS.items():
        if any(kw in text_lower for kw in keywords):
            return cluster
    return "General"

def fetch_team_posts(team_name, team_data, limit=50):
    """Fetch Bluesky posts for a team using two queries, deduplicated."""
    all_posts = []
    seen_uris = set()
    queries = [
        f"{team_name} WorldCup2026",
        f"{team_name} FIFA2026",
    ]
    for query in queries:
        try:
            resp = requests.get(
                BLUESKY_API,
                params={"q": query, "limit": limit},
                timeout=10,
            )
            resp.raise_for_status()
            posts = resp.json().get("posts", [])
            for post in posts:
                uri = post.get("uri", "")
                if uri not in seen_uris:
                    seen_uris.add(uri)
                    all_posts.append(post)
        except Exception as e:
            print(f"  [Bluesky] Error fetching '{query}': {e}")
        time.sleep(0.5)
    return all_posts

def parse_post(post):
    """Extract the fields we care about from a raw Bluesky post object."""
    record = post.get("record", {})
    author = post.get("author", {})
    return {
        "text": record.get("text", ""),
        "likes": post.get("likeCount", 0),
        "reposts": post.get("repostCount", 0),
        "replies": post.get("replyCount", 0),
        "handle": author.get("handle", ""),
        "display_name": author.get("displayName", ""),
        "created_at": record.get("createdAt", ""),
    }

def collect_bluesky():
    print(f"\n[Bluesky] Starting collection — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    conn = get_connection()
    cursor = conn.cursor()
    captured_at = datetime.now().isoformat()
    p = ph()

    teams_with_data = 0
    all_keywords = []

    for team_name, team_data in TEAMS.items():
        raw_posts = fetch_team_posts(team_name, team_data)
        if not raw_posts:
            continue

        parsed = [parse_post(p_) for p_ in raw_posts]
        texts = [p_["text"] for p_ in parsed if p_["text"]]
        if not texts:
            continue

        # Sentiment analysis
        scores = [analyzer.polarity_scores(t) for t in texts]
        n = len(scores)
        avg_pos  = sum(s["pos"] for s in scores) / n
        avg_neg  = sum(s["neg"] for s in scores) / n
        avg_neu  = sum(s["neu"] for s in scores) / n
        avg_comp = sum(s["compound"] for s in scores) / n

        # Reach = total likes + reposts across all posts
        total_reach = sum(p_["likes"] + p_["reposts"] for p_ in parsed)

        cursor.execute(f"""
            INSERT INTO sentiment_snapshots
            (captured_at, team, source, positive, negative, neutral, compound, mention_count, reach_score)
            VALUES ({p},{p},{p},{p},{p},{p},{p},{p},{p})
        """, (captured_at, team_name, "bluesky",
              round(avg_pos, 4), round(avg_neg, 4),
              round(avg_neu, 4), round(avg_comp, 4),
              n, total_reach))

        # Extract keywords from this team's posts
        for text in texts:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            all_keywords.extend([
                (w, team_name) for w in words if w not in STOPWORDS
            ])

        teams_with_data += 1
        print(f"  {team_data['flag']} {team_name}: {n} posts, compound={avg_comp:.2f}, reach={total_reach}")

    # Save top 50 keywords globally
    word_counts = Counter(w for w, _ in all_keywords).most_common(50)
    for keyword, freq in word_counts:
        # Find team most associated with this keyword
        team_words = [t for w, t in all_keywords if w == keyword]
        top_team = Counter(team_words).most_common(1)
        team_assoc = top_team[0][0] if top_team else None
        cluster = assign_cluster(keyword)

        cursor.execute(f"""
            INSERT INTO keyword_snapshots (captured_at, keyword, frequency, team_association)
            VALUES ({p},{p},{p},{p})
        """, (captured_at, keyword, freq, team_assoc))

    conn.commit()
    conn.close()
    print(f"[Bluesky] Done — {teams_with_data} teams, {len(word_counts)} keywords saved")

if __name__ == "__main__":
    collect_bluesky()
