"""
teams.py
--------
Single source of truth for all 32 FIFA World Cup 2026 teams.
Each team has:
- search_terms: used for Bluesky post matching
- trends_query: what to search on Google Trends
- confederation: for colour coding in the dashboard
"""

TEAMS = {
    "Argentina": {
        "search_terms": ["argentina", "albiceleste", "messi", "arg"],
        "trends_query": "Argentina World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇦🇷",
    },
    "France": {
        "search_terms": ["france", "les bleus", "mbappe", "fra"],
        "trends_query": "France World Cup",
        "confederation": "UEFA",
        "flag": "🇫🇷",
    },
    "England": {
        "search_terms": ["england", "three lions", "eng"],
        "trends_query": "England World Cup",
        "confederation": "UEFA",
        "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    },
    "Brazil": {
        "search_terms": ["brazil", "brasil", "selecao", "bra"],
        "trends_query": "Brazil World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇧🇷",
    },
    "Spain": {
        "search_terms": ["spain", "la roja", "esp"],
        "trends_query": "Spain World Cup",
        "confederation": "UEFA",
        "flag": "🇪🇸",
    },
    "Germany": {
        "search_terms": ["germany", "die mannschaft", "ger"],
        "trends_query": "Germany World Cup",
        "confederation": "UEFA",
        "flag": "🇩🇪",
    },
    "Portugal": {
        "search_terms": ["portugal", "por", "ronaldo", "cristiano"],
        "trends_query": "Portugal World Cup",
        "confederation": "UEFA",
        "flag": "🇵🇹",
    },
    "Netherlands": {
        "search_terms": ["netherlands", "holland", "oranje", "ned"],
        "trends_query": "Netherlands World Cup",
        "confederation": "UEFA",
        "flag": "🇳🇱",
    },
    "USA": {
        "search_terms": ["usa", "usmnt", "united states"],
        "trends_query": "USA World Cup 2026",
        "confederation": "CONCACAF",
        "flag": "🇺🇸",
    },
    "Mexico": {
        "search_terms": ["mexico", "el tri", "mex"],
        "trends_query": "Mexico World Cup",
        "confederation": "CONCACAF",
        "flag": "🇲🇽",
    },
    "Canada": {
        "search_terms": ["canada", "canmnt"],
        "trends_query": "Canada World Cup",
        "confederation": "CONCACAF",
        "flag": "🇨🇦",
    },
    "Morocco": {
        "search_terms": ["morocco", "atlas lions", "mar"],
        "trends_query": "Morocco World Cup",
        "confederation": "CAF",
        "flag": "🇲🇦",
    },
    "Senegal": {
        "search_terms": ["senegal", "sen"],
        "trends_query": "Senegal World Cup",
        "confederation": "CAF",
        "flag": "🇸🇳",
    },
    "Japan": {
        "search_terms": ["japan", "samurai blue", "jpn"],
        "trends_query": "Japan World Cup",
        "confederation": "AFC",
        "flag": "🇯🇵",
    },
    "South Korea": {
        "search_terms": ["south korea", "korea", "kor"],
        "trends_query": "South Korea World Cup",
        "confederation": "AFC",
        "flag": "🇰🇷",
    },
    "Australia": {
        "search_terms": ["australia", "socceroos", "aus"],
        "trends_query": "Australia World Cup",
        "confederation": "AFC",
        "flag": "🇦🇺",
    },
    "Iran": {
        "search_terms": ["iran", "team melli", "iri"],
        "trends_query": "Iran World Cup",
        "confederation": "AFC",
        "flag": "🇮🇷",
    },
    "Saudi Arabia": {
        "search_terms": ["saudi arabia", "ksa", "saudi"],
        "trends_query": "Saudi Arabia World Cup",
        "confederation": "AFC",
        "flag": "🇸🇦",
    },
    "Ecuador": {
        "search_terms": ["ecuador", "ecu"],
        "trends_query": "Ecuador World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇪🇨",
    },
    "Uruguay": {
        "search_terms": ["uruguay", "uru"],
        "trends_query": "Uruguay World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇺🇾",
    },
    "Colombia": {
        "search_terms": ["colombia", "col"],
        "trends_query": "Colombia World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇨🇴",
    },
    "Switzerland": {
        "search_terms": ["switzerland", "sui"],
        "trends_query": "Switzerland World Cup",
        "confederation": "UEFA",
        "flag": "🇨🇭",
    },
    "Croatia": {
        "search_terms": ["croatia", "cro"],
        "trends_query": "Croatia World Cup",
        "confederation": "UEFA",
        "flag": "🇭🇷",
    },
    "Serbia": {
        "search_terms": ["serbia", "srb"],
        "trends_query": "Serbia World Cup",
        "confederation": "UEFA",
        "flag": "🇷🇸",
    },
    "Poland": {
        "search_terms": ["poland", "pol", "lewandowski"],
        "trends_query": "Poland World Cup",
        "confederation": "UEFA",
        "flag": "🇵🇱",
    },
    "Turkey": {
        "search_terms": ["turkey", "tur"],
        "trends_query": "Turkey World Cup",
        "confederation": "UEFA",
        "flag": "🇹🇷",
    },
    "Nigeria": {
        "search_terms": ["nigeria", "super eagles", "nga"],
        "trends_query": "Nigeria World Cup",
        "confederation": "CAF",
        "flag": "🇳🇬",
    },
    "Cameroon": {
        "search_terms": ["cameroon", "indomitable lions", "cmr"],
        "trends_query": "Cameroon World Cup",
        "confederation": "CAF",
        "flag": "🇨🇲",
    },
    "Venezuela": {
        "search_terms": ["venezuela", "ven"],
        "trends_query": "Venezuela World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇻🇪",
    },
    "Chile": {
        "search_terms": ["chile", "chi"],
        "trends_query": "Chile World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇨🇱",
    },
    "Peru": {
        "search_terms": ["peru", "per"],
        "trends_query": "Peru World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇵🇪",
    },
    "New Zealand": {
        "search_terms": ["new zealand", "all whites", "nzl"],
        "trends_query": "New Zealand World Cup",
        "confederation": "OFC",
        "flag": "🇳🇿",
    },
}

CONFEDERATION_COLORS = {
    "UEFA":     "#378ADD",
    "CONMEBOL": "#1D9E75",
    "CONCACAF": "#E24B4A",
    "AFC":      "#EF9F27",
    "CAF":      "#D4537E",
    "OFC":      "#888780",
}

TEAM_NAMES = list(TEAMS.keys())

# Batches of 5 for Google Trends (API limit per request)
def get_trend_batches():
    batches = []
    names = TEAM_NAMES.copy()
    while names:
        batches.append(names[:5])
        names = names[5:]
    return batches
