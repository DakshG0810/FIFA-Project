import { useEffect, useState } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"

function timeAgo(iso?: string): string {
  if (!iso) return "never"
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60)   return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

export default function DataFreshnessBar() {
  const { data: status } = useApi(() => api.status(), null, 30_000)
  const [, forceUpdate] = useState(0)

  useEffect(() => {
    const id = setInterval(() => forceUpdate(n => n + 1), 10_000)
    return () => clearInterval(id)
  }, [])

  const sources = [
    { label: "Bluesky",    value: status?.last_bluesky,        color: "bg-sky-400" },
    { label: "Trends",     value: status?.last_google_trends,  color: "bg-emerald-400" },
    { label: "Odds",       value: status?.last_odds,           color: "bg-amber-400" },
  ]

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-black/80 backdrop-blur border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 py-1.5 flex items-center gap-6 overflow-x-auto">
        <span className="text-white/30 text-xs shrink-0">Data freshness</span>
        {sources.map(s => (
          <div key={s.label} className="flex items-center gap-1.5 shrink-0">
            <span className={`w-1.5 h-1.5 rounded-full ${s.value ? s.color : "bg-white/20"}`} />
            <span className="text-white/40 text-xs">{s.label}</span>
            <span className="text-white/60 text-xs">{timeAgo(s.value)}</span>
          </div>
        ))}
        {status && (
          <span className="text-white/20 text-xs ml-auto shrink-0">
            {status.total_snapshots.toLocaleString()} snapshots stored
          </span>
        )}
      </div>
    </div>
  )
}
