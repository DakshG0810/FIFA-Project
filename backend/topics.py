"""
Shared topic cluster and buzzword filter definitions.
"""

from teams import TEAMS

CLUSTERS = {
    "Injuries & fitness": ["injured", "injury", "fitness", "doubt", "out", "strain", "surgery", "recovery", "unavailable"],
    "Goals & results": ["goal", "scored", "winner", "equaliser", "result", "score", "final", "victory", "defeat", "draw"],
    "Referee & VAR": ["var", "offside", "penalty", "referee", "decision", "overturned", "foul", "card", "red", "yellow"],
    "Tactics & lineup": ["formation", "pressing", "substitution", "lineup", "tactics", "coach", "manager", "system", "squad"],
    "Fan banter": ["overrated", "bottled", "class", "elite", "fraud", "goat", "terrible", "brilliant", "deserve"],
    "Squad & transfers": ["squad", "called up", "dropped", "transfer", "contract", "captain", "selected", "roster"],
}

CLUSTER_META = {
    "Injuries & fitness": {"icon": "🏥", "id": "injuries"},
    "Goals & results": {"icon": "⚽", "id": "goals"},
    "Referee & VAR": {"icon": "🟥", "id": "referee"},
    "Tactics & lineup": {"icon": "🧠", "id": "tactics"},
    "Fan banter": {"icon": "🔥", "id": "banter"},
    "Squad & transfers": {"icon": "📰", "id": "squad"},
}

PLAYER_KEYWORDS = {
    "messi", "mbappe", "ronaldo", "lewandowski", "neymar", "kane", "vinicius", "vinícius",
    "modric", "modrić", "debruyne", "de bruyne", "salah", "haaland", "bellingham", "yamal",
    "pedri", "foden", "griezmann", "griezman", "neuer", "kimmich", "musiala", "saka",
    "rice", "palmer", "wirtz", "gavi", "rodri", "valverde", "vini", "endrick", "raphinha",
    "martinez", "martínez", "dybala", "lautaro", "alvarez", "álvarez", "osimhen", "kudus",
    "son", "minjae", "kim", "mitoma", "kubo", "pulisic", "mckennie", "reyna", "davies",
    "david", "buchanan", "lucho", "diaz", "díaz", "courtois", "alisson", "donnarumma",
    "pickford", "oblak", "courtois", "kane", "sterling", "rashford", "grealish", "mount",
    "bruno", "fernandes", "casemiro", "antony", "richarlison", "raphinha", "nunez", "núñez",
    "suarez", "suárez", "cavani", "valverde", "bentancur", "enzo", "caicedo", "mac allister",
    "szoboszlai", "gravenberch", "gakpo", "diaz", "salah", "mane", "mané",
}

EVENT_KEYWORDS = {
    "goal", "goals", "scored", "scorer", "var", "penalty", "penalties", "offside",
    "red card", "yellow card", "final", "semifinal", "semi-final", "quarterfinal",
    "quarter-final", "knockout", "group stage", "group", "draw", "fixture", "fixtures",
    "opener", "opening match", "shootout", "penalty shootout", "extra time", "stoppage",
    "full time", "halftime", "half-time", "equaliser", "equalizer", "winner", "defeat",
    "victory", "result", "score", "clean sheet", "golden boot", "assist", "free kick",
    "corner", "header", "save", "saves", "qualification", "qualifier", "playoff", "play-off",
    "world cup draw", "world cup final", "round of 32", "round of 16", "last 16",
}

EMOTION_KEYWORDS = {
    "favourite", "favorite", "favourites", "favorites", "underdog", "underdogs",
    "dark horse", "contender", "contenders", "hopeful", "hopefuls", "shock", "upset",
    "heartbreak", "euphoria", "pressure", "nerves", "confident", "optimistic", "pessimistic",
    "overrated", "underrated", "bottled", "robbed", "deserve", "brilliant", "terrible",
    "class", "elite", "fraud", "goat", "legend", "hero", "villain", "drama", "controversy",
    "hype", "excitement", "belief", "doubt", "fear", "pride", "passion", "support", "backing",
}

TACTICAL_KEYWORDS = {
    "formation", "formations", "pressing", "substitution", "substitutions", "lineup",
    "lineups", "line-up", "tactics", "tactical", "coach", "manager", "system", "squad",
    "roster", "starting xi", "starting 11", "bench", "captain", "vice-captain",
    "defensive", "attacking", "midfield", "wingback", "wing-back", "fullback", "full-back",
    "striker", "winger", "playmaker", "build-up", "counter", "counterattack", "high press",
    "low block", "possession", "transition", "set piece", "set-piece", "corner routine",
    "zonal", "man marking", "false nine", "false 9", "inverted", "overlap", "width",
}


def assign_cluster(text: str) -> str:
    text_lower = text.lower()
    for cluster, keywords in CLUSTERS.items():
        if any(kw in text_lower for kw in keywords):
            return cluster
    return "General"


def is_wc_post_text(text: str) -> bool:
    """True when a Bluesky post is plausibly World Cup / football discussion."""
    if not text or len(text.strip()) < 8:
        return False
    lower = text.lower()
    if any(x in lower for x in ("world cup", "worldcup", "fifa 2026", "fifa2026", "wc 2026", "worldcup2026")):
        return True
    if assign_cluster(text) != "General":
        return True
    return any(len(term) >= 4 and term in lower for term in TEAM_TERMS)


def keyword_category(keyword: str) -> str:
    k = keyword.lower().strip()
    if k in PLAYER_KEYWORDS or any(p in k for p in PLAYER_KEYWORDS if len(p) >= 4):
        return "players"
    if any(w in k for w in sorted(EVENT_KEYWORDS, key=len, reverse=True)):
        return "events"
    if any(w in k for w in sorted(EMOTION_KEYWORDS, key=len, reverse=True)):
        return "emotions"
    if any(w in k for w in sorted(TACTICAL_KEYWORDS, key=len, reverse=True)):
        return "tactical"
    return "all"


# ── Football-only keyword filter (Buzz / word cloud) ─────────────────────────

NON_FOOTBALL_KEYWORDS = {
    "democracy", "politics", "election", "government", "president", "parliament",
    "congress", "senate", "vote", "voting", "campaign", "republican", "democrat",
    "trump", "biden", "war", "ukraine", "israel", "gaza", "russia", "china",
    "economy", "stock", "stocks", "inflation", "recession", "tax", "taxes",
    "crypto", "bitcoin", "ethereum", "nft", "movie", "movies", "film", "music",
    "celebrity", "fashion", "recipe", "cooking", "restaurant", "hotel",
    "weather", "forecast", "covid", "vaccine", "health", "doctor", "hospital",
    "school", "university", "college", "job", "jobs", "money", "salary",
    "market", "news", "breaking", "headline", "headlines",
    "watch", "video", "videos", "live", "stream", "streaming", "youtube",
    "tiktok", "instagram", "facebook", "twitter", "reddit", "podcast",
    "words", "past", "fight", "people", "person", "thing", "things", "really",
    "just", "think", "know", "said", "says", "today", "years", "year", "month",
    "week", "time", "day", "night", "morning", "life", "love", "hate",
    "free", "download", "online", "website", "app", "apps", "phone", "iphone",
    "android", "laptop", "computer", "game", "games", "gaming", "playstation",
    "xbox", "nintendo", "anime", "cartoon", "series", "episode", "season",
    "book", "books", "novel", "art", "artist", "museum", "travel guide",
}

FOOTBALL_TERMS = (
    PLAYER_KEYWORDS
    | EVENT_KEYWORDS
    | EMOTION_KEYWORDS
    | TACTICAL_KEYWORDS
    | {
        "world", "cup", "fifa", "match", "matches", "soccer", "football",
        "stadium", "stadiums", "referee", "referees", "tournament", "tournaments",
        "host", "hosts", "host nation", "host nations", "nations", "nation",
        "confederation", "uefa", "conmebol", "concacaf", "caf", "afc", "ofc",
        "worldcup", "world cup", "fifa world cup", "wc2026", "wc 2026",
        "defender", "defenders", "keeper", "goalkeeper", "goalkeepers",
        "transfer", "selected", "called up", "call-up", "callup", "injury",
        "injured", "doubt", "fitness", "suspension", "suspended", "ban",
        "kit", "jersey", "boots", "cleats", "pitch", "turf", "grass",
        "fans", "supporters", "ultras", "chant", "chants", "anthem",
        "ticket", "tickets", "travel", "accommodation", "venue", "venues",
        "mexico city", "los angeles", "miami", "dallas", "atlanta", "seattle",
        "vancouver", "toronto", "guadalajara", "monterrey", "new york",
        "bracket", "schedule", "kickoff", "kick-off", "kick off",
    }
)

# Curated Google Trends buzz terms — (keyword, category, weight 0.3–1.0)
CURATED_TRENDS_BUZZ: list[tuple[str, str, float]] = []
for _kw in sorted(PLAYER_KEYWORDS):
    if len(_kw) >= 4:
        CURATED_TRENDS_BUZZ.append((_kw, "players", 0.75))
for _kw in (
    "world cup final", "group stage", "knockout", "penalty", "var", "golden boot",
    "qualification", "opening match", "extra time", "penalty shootout", "red card",
    "world cup draw", "semifinal", "quarterfinal", "clean sheet", "offside",
):
    CURATED_TRENDS_BUZZ.append((_kw, "events", 0.85))
for _kw in (
    "favorites", "underdogs", "dark horse", "contenders", "hype", "pressure",
    "overrated", "underrated", "shock", "upset", "hopefuls", "favourites",
):
    CURATED_TRENDS_BUZZ.append((_kw, "emotions", 0.7))
for _kw in (
    "lineup", "formation", "squad", "tactics", "starting xi", "coach", "manager",
    "substitution", "pressing", "set piece", "counterattack", "possession",
):
    CURATED_TRENDS_BUZZ.append((_kw, "tactical", 0.72))

TEAM_TERMS: set[str] = set()
for _name, _meta in TEAMS.items():
    TEAM_TERMS.add(_name.lower())
    for term in _meta.get("search_terms", []):
        TEAM_TERMS.add(term.lower())


def is_football_keyword(keyword: str) -> bool:
    """Keep only football / World Cup relevant buzz terms."""
    k = keyword.lower().strip()
    if not k or len(k) < 3 or len(k) > 48:
        return False
    if k.isdigit() or k in NON_FOOTBALL_KEYWORDS:
        return False
    if k in TEAM_TERMS or k in PLAYER_KEYWORDS or k in FOOTBALL_TERMS:
        return True
    if any(term in k for term in ("world cup", "worldcup", "fifa")):
        return True
    if any(w in k for w in EVENT_KEYWORDS | EMOTION_KEYWORDS | TACTICAL_KEYWORDS):
        return True
    if any(term in k for term in TEAM_TERMS if len(term) >= 4):
        return True
    if any(term in k for term in FOOTBALL_TERMS if len(term) >= 4):
        return True
    return False
