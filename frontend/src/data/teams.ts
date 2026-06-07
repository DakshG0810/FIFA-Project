/** All 48 FIFA World Cup 2026 teams — keep in sync with backend/teams.py */

export const WC_TEAM_COUNT = 48

export const TEAM_CONFEDERATION: Record<string, string> = {
  // AFC
  Australia: "AFC",
  Iran: "AFC",
  Iraq: "AFC",
  Japan: "AFC",
  Jordan: "AFC",
  Qatar: "AFC",
  "Saudi Arabia": "AFC",
  "South Korea": "AFC",
  Uzbekistan: "AFC",
  // CAF
  Algeria: "CAF",
  "Cabo Verde": "CAF",
  "DR Congo": "CAF",
  Egypt: "CAF",
  Ghana: "CAF",
  "Ivory Coast": "CAF",
  Morocco: "CAF",
  Senegal: "CAF",
  "South Africa": "CAF",
  Tunisia: "CAF",
  // CONCACAF
  Canada: "CONCACAF",
  Curaçao: "CONCACAF",
  Haiti: "CONCACAF",
  Mexico: "CONCACAF",
  Panama: "CONCACAF",
  USA: "CONCACAF",
  // CONMEBOL
  Argentina: "CONMEBOL",
  Brazil: "CONMEBOL",
  Colombia: "CONMEBOL",
  Ecuador: "CONMEBOL",
  Paraguay: "CONMEBOL",
  Uruguay: "CONMEBOL",
  // OFC
  "New Zealand": "OFC",
  // UEFA
  Austria: "UEFA",
  Belgium: "UEFA",
  "Bosnia and Herzegovina": "UEFA",
  Croatia: "UEFA",
  Czechia: "UEFA",
  England: "UEFA",
  France: "UEFA",
  Germany: "UEFA",
  Netherlands: "UEFA",
  Norway: "UEFA",
  Portugal: "UEFA",
  Scotland: "UEFA",
  Spain: "UEFA",
  Sweden: "UEFA",
  Switzerland: "UEFA",
  Turkey: "UEFA",
}

export const WC_TEAMS = Object.keys(TEAM_CONFEDERATION)
