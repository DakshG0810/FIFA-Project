/** ISO 3166-1 alpha-2 for flag images (flagcdn.com) — avoids Windows showing "AR" instead of 🇦🇷 */

export const TEAM_FLAG_CODE: Record<string, string> = {

  // AFC

  Australia: "au",

  Iran: "ir",

  Iraq: "iq",

  Japan: "jp",

  Jordan: "jo",

  Qatar: "qa",

  "Saudi Arabia": "sa",

  "South Korea": "kr",

  Uzbekistan: "uz",

  // CAF

  Algeria: "dz",

  "Cabo Verde": "cv",

  "DR Congo": "cd",

  Egypt: "eg",

  Ghana: "gh",

  "Ivory Coast": "ci",

  Morocco: "ma",

  Senegal: "sn",

  "South Africa": "za",

  Tunisia: "tn",

  // CONCACAF

  Canada: "ca",

  Curaçao: "cw",

  Haiti: "ht",

  Mexico: "mx",

  Panama: "pa",

  USA: "us",

  // CONMEBOL

  Argentina: "ar",

  Brazil: "br",

  Colombia: "co",

  Ecuador: "ec",

  Paraguay: "py",

  Uruguay: "uy",

  // OFC

  "New Zealand": "nz",

  // UEFA

  Austria: "at",

  Belgium: "be",

  "Bosnia and Herzegovina": "ba",

  Croatia: "hr",

  Czechia: "cz",

  England: "gb-eng",

  France: "fr",

  Germany: "de",

  Netherlands: "nl",

  Norway: "no",

  Portugal: "pt",

  Scotland: "gb-sct",

  Spain: "es",

  Sweden: "se",

  Switzerland: "ch",

  Turkey: "tr",

}



/** flagcdn only serves fixed sizes (e.g. 32x24) — dynamic w32 URLs 404 */

export type FlagSize = "sm" | "md" | "lg"



const FLAG_DIMS: Record<FlagSize, string> = {

  sm: "20x15",

  md: "32x24",

  lg: "40x30",

}



export function getFlagImageUrl(team: string, size: FlagSize = "md"): string {

  const code = TEAM_FLAG_CODE[team]

  if (!code) return ""

  return `https://flagcdn.com/${FLAG_DIMS[size]}/${code}.png`

}

