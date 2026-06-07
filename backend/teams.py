"""
teams.py
--------
Single source of truth for all 48 FIFA World Cup 2026 teams.
Each team has:
- search_terms: used for Bluesky post matching
- trends_query: what to search on Google Trends
- confederation: for colour coding in the dashboard
"""

TEAMS = {
    # ── AFC (9) ──────────────────────────────────────────────────────────────
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
    "Iraq": {
        "search_terms": ["iraq", "iraqi", "irq"],
        "trends_query": "Iraq World Cup",
        "confederation": "AFC",
        "flag": "🇮🇶",
    },
    "Japan": {
        "search_terms": ["japan", "samurai blue", "jpn"],
        "trends_query": "Japan World Cup",
        "confederation": "AFC",
        "flag": "🇯🇵",
    },
    "Jordan": {
        "search_terms": ["jordan", "jordanian", "jor"],
        "trends_query": "Jordan World Cup",
        "confederation": "AFC",
        "flag": "🇯🇴",
    },
    "Qatar": {
        "search_terms": ["qatar", "qat"],
        "trends_query": "Qatar World Cup",
        "confederation": "AFC",
        "flag": "🇶🇦",
    },
    "Saudi Arabia": {
        "search_terms": ["saudi arabia", "ksa", "saudi"],
        "trends_query": "Saudi Arabia World Cup",
        "confederation": "AFC",
        "flag": "🇸🇦",
    },
    "South Korea": {
        "search_terms": ["south korea", "korea republic", "kor"],
        "trends_query": "South Korea World Cup",
        "confederation": "AFC",
        "flag": "🇰🇷",
    },
    "Uzbekistan": {
        "search_terms": ["uzbekistan", "uzb"],
        "trends_query": "Uzbekistan World Cup",
        "confederation": "AFC",
        "flag": "🇺🇿",
    },
    # ── CAF (10) ─────────────────────────────────────────────────────────────
    "Algeria": {
        "search_terms": ["algeria", "algerian", "alg"],
        "trends_query": "Algeria World Cup",
        "confederation": "CAF",
        "flag": "🇩🇿",
    },
    "Cabo Verde": {
        "search_terms": ["cabo verde", "cape verde", "cpv"],
        "trends_query": "Cabo Verde World Cup",
        "confederation": "CAF",
        "flag": "🇨🇻",
    },
    "DR Congo": {
        "search_terms": ["dr congo", "congo dr", "drc", "leopards"],
        "trends_query": "DR Congo World Cup",
        "confederation": "CAF",
        "flag": "🇨🇩",
    },
    "Egypt": {
        "search_terms": ["egypt", "pharaohs", "egy"],
        "trends_query": "Egypt World Cup",
        "confederation": "CAF",
        "flag": "🇪🇬",
    },
    "Ghana": {
        "search_terms": ["ghana", "black stars", "gha"],
        "trends_query": "Ghana World Cup",
        "confederation": "CAF",
        "flag": "🇬🇭",
    },
    "Ivory Coast": {
        "search_terms": ["ivory coast", "cote d'ivoire", "cote divoire", "civ"],
        "trends_query": "Ivory Coast World Cup",
        "confederation": "CAF",
        "flag": "🇨🇮",
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
    "South Africa": {
        "search_terms": ["south africa", "bafana bafana", "rsa"],
        "trends_query": "South Africa World Cup",
        "confederation": "CAF",
        "flag": "🇿🇦",
    },
    "Tunisia": {
        "search_terms": ["tunisia", "tun"],
        "trends_query": "Tunisia World Cup",
        "confederation": "CAF",
        "flag": "🇹🇳",
    },
    # ── CONCACAF (6) ───────────────────────────────────────────────────────────
    "Canada": {
        "search_terms": ["canada", "canmnt"],
        "trends_query": "Canada World Cup",
        "confederation": "CONCACAF",
        "flag": "🇨🇦",
    },
    "Curaçao": {
        "search_terms": ["curacao", "curaçao", "cuw"],
        "trends_query": "Curacao World Cup",
        "confederation": "CONCACAF",
        "flag": "🇨🇼",
    },
    "Haiti": {
        "search_terms": ["haiti", "haitian", "hai"],
        "trends_query": "Haiti World Cup",
        "confederation": "CONCACAF",
        "flag": "🇭🇹",
    },
    "Mexico": {
        "search_terms": ["mexico", "el tri", "mex"],
        "trends_query": "Mexico World Cup",
        "confederation": "CONCACAF",
        "flag": "🇲🇽",
    },
    "Panama": {
        "search_terms": ["panama", "pan"],
        "trends_query": "Panama World Cup",
        "confederation": "CONCACAF",
        "flag": "🇵🇦",
    },
    "USA": {
        "search_terms": ["usa", "usmnt", "united states"],
        "trends_query": "USA World Cup 2026",
        "confederation": "CONCACAF",
        "flag": "🇺🇸",
    },
    # ── CONMEBOL (6) ───────────────────────────────────────────────────────────
    "Argentina": {
        "search_terms": ["argentina", "albiceleste", "messi", "arg"],
        "trends_query": "Argentina World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇦🇷",
    },
    "Brazil": {
        "search_terms": ["brazil", "brasil", "selecao", "bra"],
        "trends_query": "Brazil World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇧🇷",
    },
    "Colombia": {
        "search_terms": ["colombia", "col"],
        "trends_query": "Colombia World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇨🇴",
    },
    "Ecuador": {
        "search_terms": ["ecuador", "ecu"],
        "trends_query": "Ecuador World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇪🇨",
    },
    "Paraguay": {
        "search_terms": ["paraguay", "par"],
        "trends_query": "Paraguay World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇵🇾",
    },
    "Uruguay": {
        "search_terms": ["uruguay", "uru"],
        "trends_query": "Uruguay World Cup",
        "confederation": "CONMEBOL",
        "flag": "🇺🇾",
    },
    # ── OFC (1) ────────────────────────────────────────────────────────────────
    "New Zealand": {
        "search_terms": ["new zealand", "all whites", "nzl"],
        "trends_query": "New Zealand World Cup",
        "confederation": "OFC",
        "flag": "🇳🇿",
    },
    # ── UEFA (16) ──────────────────────────────────────────────────────────────
    "Austria": {
        "search_terms": ["austria", "aut"],
        "trends_query": "Austria World Cup",
        "confederation": "UEFA",
        "flag": "🇦🇹",
    },
    "Belgium": {
        "search_terms": ["belgium", "bel", "red devils"],
        "trends_query": "Belgium World Cup",
        "confederation": "UEFA",
        "flag": "🇧🇪",
    },
    "Bosnia and Herzegovina": {
        "search_terms": ["bosnia", "bosnia herzegovina", "bih"],
        "trends_query": "Bosnia World Cup",
        "confederation": "UEFA",
        "flag": "🇧🇦",
    },
    "Croatia": {
        "search_terms": ["croatia", "cro"],
        "trends_query": "Croatia World Cup",
        "confederation": "UEFA",
        "flag": "🇭🇷",
    },
    "Czechia": {
        "search_terms": ["czechia", "czech republic", "cze"],
        "trends_query": "Czechia World Cup",
        "confederation": "UEFA",
        "flag": "🇨🇿",
    },
    "England": {
        "search_terms": ["england", "three lions", "eng"],
        "trends_query": "England World Cup",
        "confederation": "UEFA",
        "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    },
    "France": {
        "search_terms": ["france", "les bleus", "mbappe", "fra"],
        "trends_query": "France World Cup",
        "confederation": "UEFA",
        "flag": "🇫🇷",
    },
    "Germany": {
        "search_terms": ["germany", "die mannschaft", "ger"],
        "trends_query": "Germany World Cup",
        "confederation": "UEFA",
        "flag": "🇩🇪",
    },
    "Netherlands": {
        "search_terms": ["netherlands", "holland", "oranje", "ned"],
        "trends_query": "Netherlands World Cup",
        "confederation": "UEFA",
        "flag": "🇳🇱",
    },
    "Norway": {
        "search_terms": ["norway", "nor"],
        "trends_query": "Norway World Cup",
        "confederation": "UEFA",
        "flag": "🇳🇴",
    },
    "Portugal": {
        "search_terms": ["portugal", "por", "ronaldo", "cristiano"],
        "trends_query": "Portugal World Cup",
        "confederation": "UEFA",
        "flag": "🇵🇹",
    },
    "Scotland": {
        "search_terms": ["scotland", "sco", "tartan army"],
        "trends_query": "Scotland World Cup",
        "confederation": "UEFA",
        "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    },
    "Spain": {
        "search_terms": ["spain", "la roja", "esp"],
        "trends_query": "Spain World Cup",
        "confederation": "UEFA",
        "flag": "🇪🇸",
    },
    "Sweden": {
        "search_terms": ["sweden", "swe"],
        "trends_query": "Sweden World Cup",
        "confederation": "UEFA",
        "flag": "🇸🇪",
    },
    "Switzerland": {
        "search_terms": ["switzerland", "sui"],
        "trends_query": "Switzerland World Cup",
        "confederation": "UEFA",
        "flag": "🇨🇭",
    },
    "Turkey": {
        "search_terms": ["turkey", "turkiye", "tur"],
        "trends_query": "Turkey World Cup",
        "confederation": "UEFA",
        "flag": "🇹🇷",
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

WC_TEAM_COUNT = len(TEAM_NAMES)

# Batches of 5 for Google Trends (API limit per request)
def get_trend_batches():
    batches = []
    names = TEAM_NAMES.copy()
    while names:
        batches.append(names[:5])
        names = names[5:]
    return batches
