import { useState, useCallback } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

const CONFEDERATION_LEGEND = [
  { label: "UEFA", color: "#378ADD" },
  { label: "CONMEBOL", color: "#1D9E75" },
  { label: "CONCACAF", color: "#E24B4A" },
  { label: "AFC", color: "#EF9F27" },
  { label: "CAF", color: "#D4537E" },
  { label: "OFC", color: "#888780" },
] as const

const ROW_HEIGHT = 22

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
  }))

  const chartHeight = Math.max(sorted.length * ROW_HEIGHT, ROW_HEIGHT * 8)

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-white font-semibold">Team Buzz Volume</h2>
            <DataBadge mode={badge} />
          </div>
          <p className="text-white/40 text-xs mt-1">Bluesky mention count · latest collection run</p>
        </div>
        <div className="relative group">
          <button
            type="button"
            onClick={() => setRelative((r) => !r)}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              relative
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "bg-white/5 text-white/50 border-white/10"
            }`}
          >
            {relative ? "Relative buzz on" : "Relative buzz"}
          </button>
          <div
            role="tooltip"
            className="pointer-events-none absolute right-0 top-full z-20 mt-2 w-64 rounded-lg border border-white/15 bg-[#0a0a0e] px-3 py-2 text-[11px] text-white/80 opacity-0 shadow-xl transition-opacity group-hover:opacity-100"
          >
            <p className="font-medium text-white mb-1">Relative buzz formula</p>
            <p className="font-mono text-emerald-400/90">current mentions ÷ 6h rolling average</p>
            <p className="text-white/50 mt-1">Values above 1× mean more buzz than the recent baseline.</p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-2">
        {CONFEDERATION_LEGEND.map(({ label, color }) => (
          <span key={label} className="inline-flex items-center gap-1.5 text-[10px] text-white/50">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: color }} />
            {label}
          </span>
        ))}
      </div>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : (
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 4, right: 16, top: 4, bottom: 4 }}>
            <XAxis type="number" tick={{ fill: "#ffffff40", fontSize: 9 }} hide={relative} />
            <YAxis
              type="category"
              dataKey="team"
              width={96}
              tick={{ fill: "#ffffff90", fontSize: 9 }}
              interval={0}
            />
            <Tooltip
              contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#fff" }}
              itemStyle={{ color: "#fff" }}
              formatter={(v: number) => [relative ? `${v}× usual` : v, relative ? "Multiplier" : "Mentions"]}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={14}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.color} fillOpacity={0.85} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
