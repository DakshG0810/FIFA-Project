import { useState, useCallback, useMemo } from "react"
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
  "#10b981", "#34d399", "#6ee7b7", "#059669",
  "#3b82f6", "#60a5fa", "#38bdf8", "#818cf8",
  "#a78bfa", "#c084fc", "#f472b6", "#fb7185",
  "#f59e0b", "#fbbf24", "#facc15", "#a3e635",
]

/** Dense packed layout — larger words first, tight grid with jitter */
function layoutDenseCloud(words: Keyword[]) {
  const sorted = [...words].sort((a, b) => b.total_freq - a.total_freq).slice(0, 90)
  const max = Math.max(...sorted.map((w) => w.total_freq), 1)
  const cols = 11
  const rows = Math.ceil(sorted.length / cols)

  return sorted.map((kw, i) => {
    const col = i % cols
    const row = Math.floor(i / cols)
    const jitterX = ((kw.keyword.charCodeAt(0) || 0) % 9) - 4
    const jitterY = ((kw.keyword.charCodeAt(1) || 0) % 7) - 3
    const cellW = 100 / cols
    const cellH = 100 / rows
    const x = col * cellW + cellW * 0.5 + jitterX * 0.35
    const y = row * cellH + cellH * 0.48 + jitterY * 0.35
    const weight = kw.total_freq / max
    const fontSize = 9 + weight * 36
    const rotation = i % 7 === 0 ? 90 : i % 11 === 0 ? -90 : ((i * 19 + kw.keyword.length) % 17) - 8
    const color = PALETTE[i % PALETTE.length]
    return { ...kw, x, y, fontSize, rotation, color, weight }
  })
}

/** Google Trends buzzword cloud only — no Bluesky, no bar chart toggle */
export default function BuzzwordCloud() {
  const [filter, setFilter] = useState<string>("all")
  const badge = useDataMode("google_trends")

  const fetchKeywords = useCallback(
    () => api.keywords(90, filter, "google_trends", 0),
    [filter]
  )
  const { data, loading } = useApi<Keyword[]>(fetchKeywords, [], 300000)
  const cloudWords = useMemo(() => layoutDenseCloud(data), [data])

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-white font-semibold">Buzzword Cloud</h2>
        <DataBadge mode={badge} />
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
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
        <p className="text-white/30 text-sm py-12 text-center">
          No Trends buzzwords yet — run the Google Trends collector
        </p>
      ) : (
        <div
          className="relative w-full max-w-full rounded-xl overflow-hidden bg-[#060608] border border-white/5"
          style={{ minHeight: Math.max(280, Math.ceil(cloudWords.length / 11) * 44) }}
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(16,185,129,0.08),transparent_65%)]" />
          {cloudWords.map((w) => (
            <span
              key={w.keyword}
              className="absolute font-bold leading-none select-none whitespace-nowrap pointer-events-none max-w-[90vw] truncate sm:max-w-none sm:truncate-none"
              style={{
                left: `${w.x}%`,
                top: `${w.y}%`,
                transform: `translate(-50%, -50%) rotate(${w.rotation}deg)`,
                fontSize: `clamp(8px, ${w.fontSize * 0.72}px, ${w.fontSize}px)`,
                color: w.color,
                opacity: 0.82 + w.weight * 0.18,
                textShadow: "0 1px 6px rgba(0,0,0,0.85)",
                zIndex: Math.round(w.weight * 10),
              }}
            >
              {w.keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
