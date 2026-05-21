import { useState, useCallback } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { Influencer } from "../types"
import TeamFlag from "./TeamFlag"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

type Tab = "all" | "amplifiers" | "critics"

export default function InfluencerTracker() {
  const badge = useDataMode("bluesky")
  const [tab, setTab] = useState<Tab>("all")

  const fetchInfluencers = useCallback(() => api.influencers(tab), [tab])
  const { data, loading } = useApi<Influencer[]>(fetchInfluencers, [], 300000)

  const tabs: { id: Tab; label: string }[] = [
    { id: "all", label: "All" },
    { id: "amplifiers", label: "Amplifiers (>75% pos)" },
    { id: "critics", label: "Critics (>75% neg)" },
  ]

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h2 className="text-white font-semibold">Influencer Tracker</h2>
          <DataBadge mode={badge} />
        </div>
        <div className="flex gap-2 flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-3 py-1 rounded-lg text-xs border ${
                tab === t.id
                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                  : "bg-white/5 text-white/50 border-white/10"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton rows={5} />
      ) : data.length === 0 ? (
        <p className="text-white/30 text-sm py-8 text-center">No influencer data — run Bluesky collector</p>
      ) : (
        <div className="grid sm:grid-cols-2 gap-3 max-h-[480px] overflow-y-auto">
          {data.map((inf, i) => (
            <div
              key={inf.handle}
              className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-white/30 text-xs font-mono">#{i + 1}</span>
                  <p className="text-white font-medium text-sm">@{inf.handle}</p>
                  <p className="text-white/40 text-xs">{inf.display_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-emerald-400 font-mono text-sm">{Math.round(inf.reach_score)}</p>
                  <p className="text-white/30 text-[10px]">reach</p>
                </div>
              </div>
              {inf.primary_team && (
                <div className="flex items-center gap-1 text-xs text-white/50">
                  <TeamFlag team={inf.primary_team} size="sm" />
                  {inf.primary_team}
                  <span
                    className={`ml-auto font-mono ${
                      inf.sentiment > 0.1 ? "text-emerald-400" : inf.sentiment < -0.1 ? "text-red-400" : "text-white/40"
                    }`}
                  >
                    {inf.sentiment >= 0 ? "+" : ""}{inf.sentiment.toFixed(2)}
                  </span>
                </div>
              )}
              <p className="text-white/50 text-xs line-clamp-2 italic">&ldquo;{inf.viral_post}&rdquo;</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
