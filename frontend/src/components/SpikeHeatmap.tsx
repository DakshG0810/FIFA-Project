import { useCallback, useMemo } from "react"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { SpikeHeatmapData } from "../types"
import TeamFlag, { getFlag } from "./TeamFlag"
import LoadingSkeleton from "./LoadingSkeleton"
import DataBadge from "./DataBadge"
import { useDataMode } from "../hooks/useDataMode"

const EMPTY: SpikeHeatmapData = { teams: [], buckets: 48, hours: 24, cells: [], max_mentions: 1 }

export default function SpikeHeatmap() {
  const badge = useDataMode("bluesky")
  const fetchHeatmap = useCallback(() => api.spikeHeatmap(), [])
  const { data, loading } = useApi(fetchHeatmap, EMPTY, 60000)

  const cellMap = useMemo(() => {
    const m = new Map<string, number>()
    for (const c of data.cells) {
      m.set(`${c.team}-${c.bucket}`, c.intensity)
    }
    return m
  }, [data.cells])

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
      <div className="flex items-center gap-2">
        <h2 className="text-white font-semibold">24h Mention Heatmap</h2>
        <DataBadge mode={badge} />
      </div>
      <p className="text-white/40 text-xs">32 teams × 48 half-hour buckets · darker = more mentions</p>

      {loading ? (
        <LoadingSkeleton rows={4} />
      ) : data.teams.length === 0 ? (
        <p className="text-white/30 text-sm py-8 text-center">Collecting mention history…</p>
      ) : (
        <div className="overflow-x-auto">
          <div className="min-w-[640px]">
            <div className="flex gap-px mb-1 pl-28">
              {Array.from({ length: 12 }).map((_, i) => (
                <span key={i} className="flex-1 text-[9px] text-white/20 text-center">
                  -{24 - i * 2}h
                </span>
              ))}
            </div>
            {data.teams.map((team) => (
              <div key={team} className="flex items-center gap-2 mb-px">
                <span className="w-24 text-xs text-white/60 truncate shrink-0" title={team}>
                  {getFlag(team)} {team}
                </span>
                <div className="flex flex-1 gap-px h-3">
                  {Array.from({ length: data.buckets }).map((_, b) => {
                    const intensity = cellMap.get(`${team}-${b}`) ?? 0
                    const alpha = 0.08 + intensity * 0.92
                    return (
                      <div
                        key={b}
                        className="flex-1 rounded-[1px] min-w-[3px]"
                        style={{ backgroundColor: `rgba(16, 185, 129, ${alpha})` }}
                        title={`${team} · bucket ${b}`}
                      />
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
