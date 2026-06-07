import { useState, useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { TopicCluster } from "../types"
import { WC_TEAMS } from "../data/teams"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

export default function TopicClusters() {
  const badge = useDataMode("bluesky")
  const [teamFilter, setTeamFilter] = useState<string>("")
  const [selected, setSelected] = useState<TopicCluster | null>(null)

  const fetchClusters = useCallback(
    () => api.clusters(teamFilter || undefined),
    [teamFilter]
  )
  const { data, loading } = useApi(fetchClusters, { clusters: [], team_filter: null }, 300000)

  const maxVol = Math.max(...data.clusters.map((c) => c.volume), 1)

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h2 className="text-white font-semibold">Topic Clusters</h2>
          <DataBadge mode={badge} />
        </div>
        <select
          value={teamFilter}
          onChange={(e) => { setTeamFilter(e.target.value); setSelected(null) }}
          className="bg-[#1a1a22] border border-white/20 text-white text-xs rounded-lg px-3 py-1.5 [&>option]:bg-[#1a1a22] [&>option]:text-white"
        >
          <option value="">All teams</option>
          {WC_TEAMS.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <LoadingSkeleton rows={4} />
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex flex-wrap gap-3 justify-center min-h-[220px] items-center p-4">
            {data.clusters.map((c) => {
              const size = 72 + (c.volume / maxVol) * 80
              return (
                <button
                  key={c.id}
                  onClick={() => setSelected(c)}
                  className={`rounded-full border flex flex-col items-center justify-center transition-all hover:scale-105 ${
                    selected?.id === c.id
                      ? "border-emerald-400 bg-emerald-500/20"
                      : "border-white/20 bg-white/5 hover:border-white/40"
                  }`}
                  style={{ width: size, height: size }}
                >
                  <span className="text-2xl">{c.icon}</span>
                  <span className="text-[10px] text-white/70 text-center px-1 leading-tight mt-1">
                    {c.name.split(" ")[0]}
                  </span>
                  <span className="text-emerald-400 font-mono text-xs">{c.volume}</span>
                </button>
              )
            })}
          </div>

          <div className="bg-black/30 border border-white/10 rounded-xl p-4 min-h-[220px]">
            {selected ? (
              <div className="space-y-3">
                <h3 className="text-white font-medium flex items-center gap-2">
                  <span>{selected.icon}</span> {selected.name}
                </h3>
                {selected.top_keywords.length > 0 && (
                  <p className="text-white/40 text-xs">
                    Keywords: {selected.top_keywords.map((k) => k.keyword).join(", ")}
                  </p>
                )}
                <p className="text-white/40 text-xs">Top posts</p>
                {selected.top_posts.length === 0 ? (
                  <p className="text-white/30 text-sm">No posts yet — run Bluesky collector</p>
                ) : (
                  selected.top_posts.map((p, i) => (
                    <div key={`${p.handle}-${i}`} className="text-sm border-b border-white/5 pb-2 last:border-0">
                      <p className="text-white/80">{p.text}</p>
                      <p className="text-white/30 text-xs mt-1">@{p.handle} · reach {p.reach}</p>
                    </div>
                  ))
                )}
              </div>
            ) : (
              <p className="text-white/30 text-sm flex items-center justify-center h-full">
                Click a bubble to see top posts
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
