import { useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { TrendsEntry } from "../types"
import BuzzwordCloud from "../components/BuzzwordCloud"
import GeographicHeatmap from "../components/GeographicHeatmap"
import TeamFlag from "../components/TeamFlag"
import LoadingSkeleton from "../components/LoadingSkeleton"
import DataBadge from "../components/DataBadge"
import { useDataMode } from "../hooks/useDataMode"
import { useIsMobile } from "../hooks/useIsMobile"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

export default function Trends() {
  const badge = useDataMode("google_trends")
  const isMobile = useIsMobile()
  const fetchTrends = useCallback(() => api.trends(), [])
  const { data: trends, loading } = useApi<TrendsEntry[]>(fetchTrends, [], 300000)

  const chartData = [...trends]
    .sort((a, b) => b.interest_score - a.interest_score)
    .map((t) => ({ team: t.team, score: t.interest_score }))

  return (
    <div className="space-y-6 sm:space-y-8 w-full max-w-full">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-3xl font-bold text-white">Search Interest</h1>
          <DataBadge mode={badge} />
        </div>
        <p className="text-white/40 text-sm mt-1">Google Trends · worldwide search & geographic heatmap</p>
      </div>

      <BuzzwordCloud />

      <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
        <h2 className="text-white font-semibold">Search interest ranking</h2>
        {loading ? (
          <LoadingSkeleton rows={6} />
        ) : (
          <>
            <div className="w-full max-w-full overflow-x-auto">
            <ResponsiveContainer width="100%" height={isMobile ? 240 : 280} minWidth={280}>
              <BarChart data={chartData} margin={{ bottom: isMobile ? 4 : 8, left: 4, right: 8 }}>
                <XAxis
                  dataKey="team"
                  tick={{ fill: "#ffffff50", fontSize: isMobile ? 8 : 9 }}
                  angle={isMobile ? -50 : -35}
                  textAnchor="end"
                  height={isMobile ? 56 : 72}
                  interval={isMobile ? 5 : 0}
                />
                <YAxis domain={[0, 100]} tick={{ fill: "#ffffff40", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8 }}
                  labelStyle={{ color: "#fff" }}
                  itemStyle={{ color: "#fff" }}
                />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={`hsl(160, 65%, ${38 + (i % 6) * 6}%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {chartData.map((team, index) => (
                <div key={team.team} className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-3">
                  <span className="text-white/30 font-mono text-xs w-6">#{index + 1}</span>
                  <TeamFlag team={team.team} size="sm" />
                  <span className="text-white text-sm flex-1">{team.team}</span>
                  <span className="text-emerald-400 font-mono font-bold">{team.score}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      <GeographicHeatmap />
    </div>
  )
}
