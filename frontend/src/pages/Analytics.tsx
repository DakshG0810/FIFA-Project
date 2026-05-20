import { useState } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import TeamFlag, { getFlag } from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend
} from "recharts"

const TEAM_COLORS = [
  "#10b981", "#3b82f6", "#f59e0b",
  "#ef4444", "#8b5cf6", "#06b6d4",
]

const ALL_TEAMS = [
  "Argentina","France","England","Brazil","Spain","Germany",
  "Portugal","Netherlands","USA","Mexico","Canada","Morocco",
]

export default function Analytics() {
  const [selected, setSelected] = useState<string[]>(["Argentina", "France", "England", "Brazil"])

  // Fetch history for all selected teams
  const histories = selected.map(team => {
    const { data } = useApi(() => api.teamHistory(team), [], 120_000)
    return { team, data }
  })

  // Build combined chart data
  const timeMap: Record<string, any> = {}
  histories.forEach(({ team, data }) => {
    data.forEach((h: any) => {
      const key = h.captured_at.substring(0, 13)
      if (!timeMap[key]) timeMap[key] = { time: key }
      timeMap[key][team] = parseFloat((h.compound || 0).toFixed(3))
    })
  })
  const chartData = Object.values(timeMap).sort((a, b) => a.time.localeCompare(b.time))

  const toggleTeam = (team: string) => {
    setSelected(prev =>
      prev.includes(team)
        ? prev.filter(t => t !== team)
        : prev.length < 4 ? [...prev, team] : prev
    )
  }

  // Divergence: sentiment rank vs odds rank
  const { data: leaderboard } = useApi(() => api.leaderboard(), [], 120_000)
  const { data: odds }        = useApi(() => api.odds(), [], 3_600_000)

  const sentimentRanked = [...leaderboard]
    .sort((a: any, b: any) => (b.compound || 0) - (a.compound || 0))
    .map((t: any, i) => ({ team: t.team, sentimentRank: i + 1 }))

  const oddsRanked = [...odds]
    .sort((a: any, b: any) => (b.win_probability || 0) - (a.win_probability || 0))
    .map((t: any, i) => ({ team: t.team, oddsRank: i + 1 }))

  const divergence = sentimentRanked
    .map(s => {
      const o = oddsRanked.find(x => x.team === s.team)
      if (!o) return null
      return { team: s.team, sentimentRank: s.sentimentRank, oddsRank: o.oddsRank, delta: o.oddsRank - s.sentimentRank }
    })
    .filter(Boolean)
    .sort((a: any, b: any) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 10)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Analytics</h1>
        <p className="text-white/40 text-sm">Narrative shift · Sentiment vs odds divergence · Deep comparisons</p>
      </div>

      {/* Narrative shift chart */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
        <div>
          <h2 className="text-white font-semibold mb-1">Narrative shift</h2>
          <p className="text-white/30 text-xs">Select up to 4 teams to compare sentiment over time</p>
        </div>

        {/* Team selector */}
        <div className="flex flex-wrap gap-2">
          {ALL_TEAMS.map((team, i) => {
            const isSelected = selected.includes(team)
            const colorIndex = selected.indexOf(team)
            return (
              <button
                key={team}
                onClick={() => toggleTeam(team)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs border transition-all ${
                  isSelected
                    ? "border-transparent text-black font-medium"
                    : "bg-white/5 border-white/10 text-white/50 hover:text-white"
                }`}
                style={isSelected ? { background: TEAM_COLORS[colorIndex] } : {}}
              >
                {getFlag(team)} {team}
              </button>
            )
          })}
        </div>

        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <XAxis dataKey="time" tick={{ fill: "#ffffff30", fontSize: 9 }} />
              <YAxis domain={[-1, 1]} tick={{ fill: "#ffffff30", fontSize: 10 }} />
              <Tooltip
                contentStyle={{ background: "#0a0a0a", border: "1px solid #ffffff20", borderRadius: 8 }}
              />
              <ReferenceLine y={0} stroke="#ffffff15" strokeDasharray="3 3" />
              <Legend wrapperStyle={{ fontSize: 12, color: "#ffffff60" }} />
              {selected.map((team, i) => (
                <Line
                  key={team}
                  type="monotone"
                  dataKey={team}
                  stroke={TEAM_COLORS[i]}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-40 flex items-center justify-center text-white/20 text-sm">
            Sentiment history will appear after a few collection cycles
          </div>
        )}
      </div>

      {/* Sentiment vs Odds divergence */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
        <div>
          <h2 className="text-white font-semibold mb-1">Sentiment vs odds divergence ⚡</h2>
          <p className="text-white/30 text-xs">
            Where fans and bookmakers disagree most — the most analytically interesting signal
          </p>
        </div>

        {divergence.length === 0 ? (
          <div className="py-8 text-center text-white/20 text-sm">
            Needs both sentiment and odds data — check back after first collection
          </div>
        ) : (
          <div className="space-y-2">
            {divergence.map((d: any) => {
              const fansHigher = d.delta > 0
              return (
                <div
                  key={d.team}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 border ${
                    Math.abs(d.delta) >= 5
                      ? "bg-amber-500/10 border-amber-500/20"
                      : "bg-white/5 border-white/5"
                  }`}
                >
                  <TeamFlag team={d.team} size="sm" />
                  <span className="text-white text-sm font-medium w-24 shrink-0">{d.team}</span>
                  <div className="flex-1 flex items-center gap-3 text-xs">
                    <span className="text-white/40">Sentiment rank: <span className="text-white">#{d.sentimentRank}</span></span>
                    <span className="text-white/40">Odds rank: <span className="text-white">#{d.oddsRank}</span></span>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-lg ${
                    fansHigher
                      ? "bg-emerald-500/20 text-emerald-400"
                      : "bg-red-500/20 text-red-400"
                  }`}>
                    {fansHigher ? "Fans rank higher" : "Fans rank lower"} by {Math.abs(d.delta)}
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
