import { useState, useCallback, useMemo } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { Keyword } from "../types"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

const FILTERS = [
  { id: "all", label: "All" },
  { id: "players", label: "Players" },
  { id: "events", label: "Match events" },
  { id: "emotions", label: "Emotions" },
  { id: "tactical", label: "Tactical" },
] as const

const PALETTE = [
  "#10b981", "#34d399", "#6ee7b7", "#3b82f6", "#60a5fa",
  "#f59e0b", "#fbbf24", "#a78bfa", "#f472b6", "#38bdf8",
]

/** Golden-angle spiral — size by frequency, position not sorted by size */
function layoutCloud(words: Keyword[]) {
  const max = Math.max(...words.map((w) => w.total_freq), 1)
  const golden = 2.399963229728653
  const shuffled = [...words].sort((a, b) => {
    const ha = a.keyword.charCodeAt(0) % 7
    const hb = b.keyword.charCodeAt(0) % 7
    return ha - hb
  })

  return shuffled.map((kw, i) => {
    const angle = i * golden
    const radius = 28 + Math.sqrt(i + 1) * 22
    const fontSize = 11 + (kw.total_freq / max) * 34
    const x = 50 + Math.cos(angle) * radius * 0.85
    const y = 50 + Math.sin(angle) * radius * 0.55
    const rotation = ((i * 17) % 7) - 3
    const color = PALETTE[i % PALETTE.length]
    return { ...kw, x, y, fontSize, rotation, color }
  })
}

export default function BuzzwordCloud() {
  const [filter, setFilter] = useState<string>("all")
  const [barMode, setBarMode] = useState(false)
  const badge = useDataMode("bluesky")

  const fetchKeywords = useCallback(() => api.keywords(45, filter), [filter])
  const { data, loading } = useApi<Keyword[]>(fetchKeywords, [], 300000)

  const cloudWords = useMemo(() => layoutCloud(data.slice(0, 40)), [data])

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h2 className="text-white font-semibold">Buzzword Heatmap</h2>
          <DataBadge mode={badge} />
        </div>
        <button
          onClick={() => setBarMode((b) => !b)}
          className="text-xs px-3 py-1.5 rounded-lg border bg-white/5 text-white/50 border-white/10 hover:text-white"
        >
          {barMode ? "Word cloud" : "Bar chart"}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`px-3 py-1 rounded-lg text-xs border transition-all ${
              filter === f.id
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "bg-white/5 text-white/50 border-white/10"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSkeleton rows={5} />
      ) : data.length === 0 ? (
        <p className="text-white/30 text-sm py-12 text-center">No keywords yet — run Bluesky collector</p>
      ) : barMode ? (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={[...data].sort((a, b) => b.total_freq - a.total_freq).slice(0, 20)} layout="vertical" margin={{ left: 8 }}>
            <XAxis type="number" tick={{ fill: "#ffffff40", fontSize: 10 }} />
            <YAxis type="category" dataKey="keyword" width={90} tick={{ fill: "#ffffff70", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#111", border: "1px solid #333" }} />
            <Bar dataKey="total_freq" radius={[0, 4, 4, 0]}>
              {[...data].slice(0, 20).map((_, i) => (
                <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="relative w-full h-[320px] bg-[radial-gradient(ellipse_at_center,_rgba(16,185,129,0.06),transparent_70%)] rounded-xl overflow-hidden">
          {cloudWords.map((w) => (
            <span
              key={w.keyword}
              className="absolute font-semibold hover:scale-110 transition-transform cursor-default select-none"
              style={{
                left: `${w.x}%`,
                top: `${w.y}%`,
                transform: `translate(-50%, -50%) rotate(${w.rotation}deg)`,
                fontSize: `${w.fontSize}px`,
                color: w.color,
                opacity: 0.88,
                textShadow: "0 2px 8px rgba(0,0,0,0.6)",
              }}
              title={`${w.total_freq} mentions · ${w.team_association || "global"}`}
            >
              {w.keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
