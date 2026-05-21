/** ISO 3166-1 alpha-2 for flag images (flagcdn.com) — avoids Windows showing "AR" instead of 🇦🇷 */
export const TEAM_FLAG_CODE: Record<string, string> = {
  Argentina: "ar",
  France: "fr",
  England: "gb",
  Brazil: "br",
  Spain: "es",
  Germany: "de",
  Portugal: "pt",
  Netherlands: "nl",
  USA: "us",
  Mexico: "mx",
  Canada: "ca",
  Morocco: "ma",
  Senegal: "sn",
  Japan: "jp",
  "South Korea": "kr",
  Australia: "au",
  Iran: "ir",
  "Saudi Arabia": "sa",
  Ecuador: "ec",
  Uruguay: "uy",
  Colombia: "co",
  Switzerland: "ch",
  Croatia: "hr",
  Serbia: "rs",
  Poland: "pl",
  Turkey: "tr",
  Nigeria: "ng",
  Cameroon: "cm",
  Venezuela: "ve",
  Chile: "cl",
  Peru: "pe",
  "New Zealand": "nz",
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
