import type { TeamSentiment } from "../types"

/** Never show these as bookmaker favourite above a tiny implied %. */
const IMPLAUSIBLE_FAVOURITES = new Set([
  "DR Congo", "Cabo Verde", "Haiti", "Jordan", "Iraq", "Uzbekistan",
  "Curaçao", "Panama", "New Zealand", "Bosnia and Herzegovina",
  "Czechia", "Scotland", "Norway", "Sweden", "Switzerland",
])

export function pickBookmakerFavourite(rows: TeamSentiment[]): TeamSentiment | undefined {
  const eligible = rows.filter((t) => {
    const p = t.win_probability
    if (p == null || p <= 0 || p > 0.22) return false
    if (IMPLAUSIBLE_FAVOURITES.has(t.team) && p > 0.03) return false
    return true
  })
  if (!eligible.length) return undefined
  return [...eligible].sort((a, b) => (b.win_probability || 0) - (a.win_probability || 0))[0]
}
