import { useState, useCallback, useMemo } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import TeamFlag, { getFlag } from "../components/TeamFlag"
import TopicClusters from "../components/TopicClusters"
import GeographicHeatmap from "../components/GeographicHeatmap"
import InfluencerTracker from "../components/InfluencerTracker"
import DataBadge from "../components/DataBadge"
import { useDataMode } from "../hooks/useDataMode"
import type { TeamSentiment } from "../types"
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Legend,
} from "recharts"

const TEAM_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
const ALL_TEAMS = [
  "Argentina", "France", "England", "Brazil", "Spain", "Germany", "Portugal", "Netherlands",
  "USA", "Mexico", "Japan", "Morocco",
]

export default function Analytics() {
  const badge = useDataMode("bluesky")
  const [selected, setSelected] = useState(["Argentina", "France", "England", "Brazil"])

  const fetchLeaderboard = useCallback(() => api.leaderboard(), [])
  const fetchOdds = useCallback(() => api.odds(), [])
  const fetchNarrative = useCallback(() => api.narrative(selected), [selected])

  const { data: leaderboard } = useApi<TeamSentiment[]>(fetchLeaderboard, [], 120000)
  const { data: odds } = useApi(fetchOdds, [], 120000)
  const { data: narrative, loading: narrativeLoading } = useApi(fetchNarrative, { teams: [], points: [] }, 120000)

  const chartData = useMemo(() => {
    return narrative.points.map((p) => {
      const row: Record<string, string | number> = {
        time: new Date(p.time + ":00:00").toLocaleString("en", { month: "short", day: "numeric", hour: "2-digit" }),
      }
      for (const team of narrative.teams) {
        if (typeof p[team] === "number") row[team] = p[team] as number
      }
      return row
    })
  }, [narrative])

  const toggleTeam = (team: string) => {
    setSelected((prev) => {
      if (prev.includes(team)) return prev.filter((t) => t !== team)
      if (prev.length >= 4) return prev
      return [...prev, team]
    })
  }

  const sentimentRanked = [...leaderboard]
    .sort((a, b) => (b.compound || 0) - (a.compound || 0))
    .map((t, i) => ({ team: t.team, sentimentRank: i + 1 }))

  const oddsRanked = [...odds]
    .sort((a, b) => (b.win_probability || 0) - (a.win_probability || 0))
    .map((t, i) => ({ team: t.team, oddsRank: i + 1 }))

  const divergence = sentimentRanked
    .map((s) => {
      const o = oddsRanked.find((x) => x.team === s.team)
      if (!o) return null
      return { team: s.team, sentimentRank: s.sentimentRank, oddsRank: o.oddsRank, delta: o.oddsRank - s.sentimentRank }
    })
    .filter(Boolean)
    .sort((a, b) => Math.abs(b!.delta) - Math.abs(a!.delta))
    .slice(0, 10)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>
        <p className="text-white/40 text-sm">Topic clusters · Geographic search · Influencers · Narrative shift</p>
      </div>

      <TopicClusters />
      <GeographicHeatmap />
      <InfluencerTracker />

      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
        <div className="flex items-center gap-2">
          <h2 className="text-white font-semibold">Narrative Shift</h2>
          <DataBadge mode={badge} />
        </div>
        <p className="text-white/40 text-xs">Compound sentiment · up to 4 teams · hourly buckets (7 days)</p>

        <div className="flex flex-wrap gap-2">
          {ALL_TEAMS.map((team) => {
            const isSelected = selected.includes(team)
            const colorIndex = selected.indexOf(team)
            return (
              <button
                key={team}
                onClick={() => toggleTeam(team)}
                className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
                  isSelected ? "text-black border-transparent" : "bg-white/5 border-white/10 text-white/60"
                }`}
                style={isSelected ? { background: TEAM_COLORS[colorIndex] } : {}}
              >
                {getFlag(team)} {team}
              </button>
            )
          })}
        </div>

        {narrativeLoading ? (
          <div className="h-[300px] bg-white/5 rounded-lg animate-pulse" />
        ) : chartData.length === 0 ? (
          <p className="text-white/30 text-sm py-12 text-center">No narrative history yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <XAxis dataKey="time" tick={{ fill: "#ffffff40", fontSize: 9 }} interval="preserveStartEnd" />
              <YAxis domain={[-1, 1]} tick={{ fill: "#ffffff40", fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#111", border: "1px solid #333" }} />
              <Legend />
              <ReferenceLine y={0} stroke="#ffffff20" strokeDasharray="3 3" />
              {selected.map((team, i) => (
                <Line key={team} type="monotone" dataKey={team} stroke={TEAM_COLORS[i]} strokeWidth={2} dot={false} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
        <h2 className="text-white font-semibold">Sentiment vs Odds Divergence</h2>
        <p className="text-white/40 text-xs">⚡ when fan rank and odds rank differ by more than 5 positions</p>
        {divergence.length === 0 ? (
          <p className="text-white/20 text-sm py-8 text-center">Waiting for live data…</p>
        ) : (
          <div className="space-y-2">
            {divergence.map((d) => {
              const fansHigher = d!.delta > 0
              const bigGap = Math.abs(d!.delta) > 5
              return (
                <div key={d!.team} className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 flex items-center gap-3">
                  <TeamFlag team={d!.team} size="sm" />
                  <div className="flex-1">
                    <div className="text-white text-sm font-medium flex items-center gap-2">
                      {d!.team}
                      {bigGap && <span className="text-amber-400" title="Large divergence">⚡</span>}
                    </div>
                    <div className="text-white/40 text-xs">Sentiment #{d!.sentimentRank} · Odds #{d!.oddsRank}</div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-lg ${fansHigher ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>
                    {fansHigher ? "Fans more optimistic" : "Bookmakers more optimistic"}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
