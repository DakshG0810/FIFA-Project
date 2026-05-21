"""
Shared topic cluster and buzzword filter definitions.
"""

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
    "messi", "mbappe", "ronaldo", "lewandowski", "neymar", "kane", "vinicius",
    "modric", "debruyne", "salah", "haaland", "bellingham", "yamal", "pedri",
}

EVENT_KEYWORDS = {"goal", "scored", "var", "penalty", "offside", "red", "yellow", "final", "winner"}
EMOTION_KEYWORDS = {"brilliant", "terrible", "robbed", "bottled", "class", "elite", "fraud", "goat", "overrated"}
TACTICAL_KEYWORDS = {"formation", "pressing", "substitution", "lineup", "tactics", "coach", "manager", "system"}


def assign_cluster(text: str) -> str:
    text_lower = text.lower()
    for cluster, keywords in CLUSTERS.items():
        if any(kw in text_lower for kw in keywords):
            return cluster
    return "General"


def keyword_category(keyword: str) -> str:
    k = keyword.lower()
    if k in PLAYER_KEYWORDS:
        return "players"
    if any(w in k for w in EVENT_KEYWORDS):
        return "events"
    if any(w in k for w in EMOTION_KEYWORDS):
        return "emotions"
    if any(w in k for w in TACTICAL_KEYWORDS):
        return "tactical"
    return "all"
