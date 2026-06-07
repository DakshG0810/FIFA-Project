import type { TeamSentiment } from "../types"

/** Enough posts to avoid small-sample leaders (e.g. one glowing tweet). */
export function minMentionsThreshold(rows: TeamSentiment[]): number {
  const top = Math.max(...rows.map((r) => r.mentions || 0), 0)
  return Math.max(20, Math.floor(top * 0.05))
}

/** Fan favourite = highest positive Bluesky tone among teams with sufficient posts. */
export function pickFanFavourite(rows: TeamSentiment[]): TeamSentiment | undefined {
  if (!rows.length) return undefined
  const minM = minMentionsThreshold(rows)
  const eligible = rows.filter((t) => (t.mentions || 0) >= minM)
  if (!eligible.length) return undefined
  return [...eligible].sort((a, b) => {
    const byPositive = (b.positive || 0) - (a.positive || 0)
    if (Math.abs(byPositive) > 0.002) return byPositive
    return (b.compound || 0) - (a.compound || 0)
  })[0]
}

export function fanFavouriteSub(team: TeamSentiment): string {
  const posPct = Math.round((team.positive || 0) * 100)
  const comp = team.compound || 0
  return `${posPct}% positive words · ${comp >= 0 ? "+" : ""}${comp.toFixed(2)} sentiment`
}
