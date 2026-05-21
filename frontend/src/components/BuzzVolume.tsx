import { useState, useCallback } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { BuzzTeam } from "../types"
import TeamFlag from "./TeamFlag"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data, 1)
  return (
    <div className="flex items-end gap-px h-6 w-20">
      {data.slice(-12).map((v, i) => (
        <div
          key={i}
          className="flex-1 rounded-sm min-w-[2px]"
          style={{ height: `${Math.max(8, (v / max) * 100)}%`, backgroundColor: color, opacity: 0.85 }}
        />
      ))}
    </div>
  )
}

export default function BuzzVolume() {
  const badge = useDataMode("bluesky")
  const [relative, setRelative] = useState(false)
  const fetchBuzz = useCallback(() => api.buzz(), [])
  const { data, loading } = useApi(fetchBuzz, [], 60000)

  const sorted = [...data].sort((a, b) => {
    if (relative) return b.relative_multiplier - a.relative_multiplier
    return b.mentions - a.mentions
  })

  const chartData = sorted.map((t) => ({
    team: t.team,
    value: relative ? t.relative_multiplier : t.mentions,
    color: t.confederation_color,
    label: relative ? `${t.relative_multiplier}×` : t.mentions,
  }))

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-white font-semibold">Team Buzz Volume</h2>
            <DataBadge mode={badge} />
          </div>
          <p className="text-white/40 text-xs mt-1">Bluesky mention count · confederation colours</p>
        </div>
        <button
          onClick={() => setRelative((r) => !r)}
          className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
            relative
              ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
              : "bg-white/5 text-white/50 border-white/10"
          }`}
        >
          {relative ? "Relative buzz on" : "Relative buzz"}
        </button>
      </div>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : (
        <>
          <ResponsiveContainer width="100%" height={Math.min(sorted.length * 28, 520)}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24 }}>
              <XAxis type="number" tick={{ fill: "#ffffff40", fontSize: 10 }} hide={relative} />
              <YAxis type="category" dataKey="team" width={100} tick={{ fill: "#ffffff80", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8 }}
                formatter={(v: number) => [relative ? `${v}× usual` : v, relative ? "Multiplier" : "Mentions"]}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <div className="space-y-1 max-h-64 overflow-y-auto">
            {sorted.slice(0, 12).map((t: BuzzTeam) => (
              <div key={t.team} className="flex items-center gap-3 py-1.5 border-b border-white/5 last:border-0">
                <TeamFlag team={t.team} size="sm" />
                <span className="text-white text-sm w-24 shrink-0">{t.team}</span>
                <MiniSparkline data={t.sparkline} color={t.confederation_color} />
                <span className="text-white/40 text-xs font-mono ml-auto">
                  {relative ? (
                    <span className="text-emerald-400">{t.relative_multiplier}× usual</span>
                  ) : (
                    `${t.mentions} posts`
                  )}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
