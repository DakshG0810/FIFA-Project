import { useCallback, useMemo } from "react"

import { useApi } from "../hooks/useApi"

import { api } from "../api"

import type { SpikeHeatmapData } from "../types"

import TeamFlag from "./TeamFlag"

import LoadingSkeleton from "./LoadingSkeleton"

import DataBadge from "./DataBadge"

import { useDataMode } from "../hooks/useDataMode"



const EMPTY: SpikeHeatmapData = { teams: [], buckets: 0, dates: [], cells: [], max_mentions: 1 }



function formatDay(isoDate: string) {

  const d = new Date(isoDate + "T12:00:00")

  return d.toLocaleDateString("en", { month: "short", day: "numeric" })

}



export default function SpikeHeatmap() {

  const badge = useDataMode("bluesky")

  const fetchHeatmap = useCallback(() => api.spikeHeatmap(), [])

  const { data, loading } = useApi(fetchHeatmap, EMPTY, 60000)



  const cellMap = useMemo(() => {

    const m = new Map<string, { intensity: number; mentions: number }>()

    for (const c of data.cells) {

      m.set(`${c.team}-${c.bucket}`, { intensity: c.intensity, mentions: c.mentions })

    }

    return m

  }, [data.cells])



  const dates = data.dates ?? []



  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">

      <div className="flex items-center gap-2">

        <h2 className="text-white font-semibold">Mention Heatmap by Day</h2>

        <DataBadge mode={badge} />

      </div>

      <p className="text-white/40 text-xs">
        32 teams × Collection days
        {data.first_collection_date && data.last_collection_date ? (
          <> · {formatDay(data.first_collection_date)} – {formatDay(data.last_collection_date)}</>
        ) : null}
        {dates.length > 0 ? (
          <> · {dates.length} day{dates.length !== 1 ? "s" : ""} (adds 1 column after each daily run)</>
        ) : null}
      </p>



      {loading ? (

        <LoadingSkeleton rows={4} />

      ) : data.teams.length === 0 || dates.length === 0 ? (

        <p className="text-white/30 text-sm py-8 text-center">Collecting mention history…</p>

      ) : (

        <div className="overflow-x-auto">

          <div style={{ minWidth: Math.max(480, dates.length * 36 + 120) }}>

            <div className="flex gap-px mb-1 pl-[7.5rem]">

              {dates.map((day) => (

                <span

                  key={day}

                  className="flex-1 min-w-[28px] text-[9px] text-white/40 text-center truncate"

                  title={day}

                >

                  {formatDay(day)}

                </span>

              ))}

            </div>

            {data.teams.map((team) => (

              <div key={team} className="flex items-center gap-2 mb-px">

                <span className="w-[7.5rem] text-[10px] text-white/70 truncate shrink-0 flex items-center gap-1" title={team}>
                  <TeamFlag team={team} size="sm" />
                  {team}
                </span>

                <div className="flex flex-1 gap-px h-3">

                  {dates.map((day, b) => {

                    const cell = cellMap.get(`${team}-${b}`)

                    const intensity = cell?.intensity ?? 0

                    const mentions = cell?.mentions ?? 0

                    const alpha = 0.08 + intensity * 0.92

                    return (

                      <div

                        key={day}

                        className="flex-1 min-w-[28px] rounded-[1px]"

                        style={{ backgroundColor: `rgba(16, 185, 129, ${alpha})` }}

                        title={`${team} · ${formatDay(day)} · ${mentions} posts`}

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


