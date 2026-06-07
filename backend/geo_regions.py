"""
Geographic heatmap: country coverage, team home ISO codes, confederation affinity.
"""

from teams import TEAMS, TEAM_NAMES

# Team → home country ISO (participant nations)
TEAM_HOME_ISO: dict[str, str] = {
    "Argentina": "AR", "Australia": "AU", "Austria": "AT", "Belgium": "BE",
    "Bosnia and Herzegovina": "BA", "Brazil": "BR", "Canada": "CA", "Cabo Verde": "CV",
    "Colombia": "CO", "Croatia": "HR", "Curaçao": "CW", "Czechia": "CZ",
    "DR Congo": "CD", "Ecuador": "EC", "Egypt": "EG", "England": "GB",
    "France": "FR", "Germany": "DE", "Ghana": "GH", "Haiti": "HT",
    "Iran": "IR", "Iraq": "IQ", "Ivory Coast": "CI", "Japan": "JP",
    "Jordan": "JO", "Mexico": "MX", "Morocco": "MA", "Netherlands": "NL",
    "New Zealand": "NZ", "Norway": "NO", "Panama": "PA", "Paraguay": "PY",
    "Portugal": "PT", "Qatar": "QA", "Saudi Arabia": "SA", "Scotland": "GB",
    "Senegal": "SN", "South Africa": "ZA", "South Korea": "KR", "Spain": "ES",
    "Sweden": "SE", "Switzerland": "CH", "Tunisia": "TN", "Turkey": "TR",
    "USA": "US", "Uruguay": "UY", "Uzbekistan": "UZ", "Algeria": "DZ",
}

# Countries shown on map (expanded — all participant homes + major markets)
COUNTRY_CODES = sorted(set([
    "US", "CA", "MX", "BR", "AR", "CO", "UY", "EC", "PY", "CL", "PE", "VE",
    "GB", "FR", "DE", "ES", "IT", "PT", "NL", "BE", "CH", "AT", "HR", "RS",
    "TR", "PL", "SE", "NO", "DK", "IE", "CZ", "HU", "GR", "UA", "BA",
    "MA", "SN", "NG", "CM", "EG", "ZA", "CI", "GH", "DZ", "TN", "CD", "CV",
    "JP", "KR", "CN", "IN", "AU", "NZ", "SA", "IR", "QA", "IQ", "JO", "UZ",
    "TH", "VN", "PH", "ID", "MY", "PK", "BD", "IL", "RU", "HT", "PA", "CW",
]))

COUNTRY_NAMES = {
    "US": "United States", "CA": "Canada", "MX": "Mexico", "BR": "Brazil",
    "AR": "Argentina", "GB": "United Kingdom", "FR": "France", "DE": "Germany",
    "ES": "Spain", "IT": "Italy", "PT": "Portugal", "NL": "Netherlands",
    "BE": "Belgium", "CH": "Switzerland", "PL": "Poland", "SE": "Sweden",
    "NO": "Norway", "DK": "Denmark", "IE": "Ireland", "AT": "Austria",
    "HR": "Croatia", "RS": "Serbia", "TR": "Turkey", "BA": "Bosnia and Herzegovina",
    "MA": "Morocco", "SN": "Senegal", "NG": "Nigeria", "CM": "Cameroon",
    "EG": "Egypt", "ZA": "South Africa", "CI": "Ivory Coast", "GH": "Ghana",
    "DZ": "Algeria", "TN": "Tunisia", "CD": "DR Congo", "CV": "Cabo Verde",
    "JP": "Japan", "KR": "South Korea", "CN": "China", "IN": "India",
    "AU": "Australia", "NZ": "New Zealand", "SA": "Saudi Arabia", "IR": "Iran",
    "QA": "Qatar", "IQ": "Iraq", "JO": "Jordan", "UZ": "Uzbekistan",
    "EC": "Ecuador", "CO": "Colombia", "UY": "Uruguay", "PY": "Paraguay",
    "CL": "Chile", "PE": "Peru", "VE": "Venezuela", "HT": "Haiti", "PA": "Panama",
    "CW": "Curaçao", "CZ": "Czechia", "HU": "Hungary", "GR": "Greece",
    "UA": "Ukraine", "RU": "Russia", "IL": "Israel", "TH": "Thailand",
    "VN": "Vietnam", "PH": "Philippines", "ID": "Indonesia", "MY": "Malaysia",
    "PK": "Pakistan", "BD": "Bangladesh",
}

# Primary regions per confederation (for fallback weighting)
CONFED_COUNTRY_AFFINITY: dict[str, set[str]] = {
    "UEFA": {"GB", "FR", "DE", "ES", "IT", "PT", "NL", "BE", "CH", "AT", "HR", "TR", "PL", "SE", "NO", "DK", "IE", "CZ", "HU", "GR", "UA", "RS", "BA"},
    "CONMEBOL": {"BR", "AR", "CO", "UY", "EC", "PY", "CL", "PE", "VE"},
    "CONCACAF": {"US", "CA", "MX", "HT", "PA", "CW", "JM"},
    "CAF": {"MA", "SN", "NG", "EG", "ZA", "CI", "GH", "DZ", "TN", "CD", "CV", "CM"},
    "AFC": {"JP", "KR", "SA", "IR", "QA", "AU", "IN", "CN", "TH", "ID", "MY", "IQ", "JO", "UZ"},
    "OFC": {"AU", "NZ"},
}

# Rotate ~8 geos per daily collection — all map countries covered over 8 days
GEO_ROTATION_BATCHES = [
    ["US", "CA", "MX", "BR", "AR", "GB", "FR", "DE"],
    ["ES", "IT", "PT", "NL", "BE", "CH", "AT", "HR"],
    ["TR", "PL", "SE", "NO", "DK", "IE", "CZ", "GR"],
    ["UA", "RS", "BA", "RU", "IL", "EG", "MA", "ZA"],
    ["NG", "SN", "CI", "GH", "DZ", "TN", "CD", "CV"],
    ["CM", "JP", "KR", "CN", "IN", "AU", "NZ", "SA"],
    ["IR", "QA", "IQ", "JO", "UZ", "TH", "ID", "MY"],
    ["PK", "BD", "PH", "VN", "CO", "UY", "EC", "PY"],
    ["CL", "PE", "VE", "HT", "PA", "CW", "HU", "CM"],
]


def confed_boost(team: str, country_code: str) -> float:
    conf = TEAMS.get(team, {}).get("confederation", "UEFA")
    primary = CONFED_COUNTRY_AFFINITY.get(conf, set())
    if country_code in primary:
        return 1.0
    if country_code == TEAM_HOME_ISO.get(team):
        return 1.0
    return 0.25


def geos_for_today() -> list[str]:
    from datetime import datetime
    idx = datetime.now().toordinal() % len(GEO_ROTATION_BATCHES)
    return GEO_ROTATION_BATCHES[idx]


def all_map_geos() -> list[str]:
    """Every country ISO shown on the geographic heatmap."""
    return list(COUNTRY_CODES)
