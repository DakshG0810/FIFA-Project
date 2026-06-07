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



function layoutWrapCloud(words: Keyword[]) {

  const sorted = [...words].sort((a, b) => b.total_freq - a.total_freq).slice(0, 60)

  const max = Math.max(...sorted.map((w) => w.total_freq), 1)

  return sorted.map((kw, i) => {

    const weight = kw.total_freq / max

    const fontSize = 12 + weight * 22

    const color = PALETTE[i % PALETTE.length]

    return { ...kw, fontSize, color, weight }

  })

}



/** Google Trends buzzword cloud only — no Bluesky, no bar chart toggle */

export default function BuzzwordCloud() {

  const [filter, setFilter] = useState<string>("all")

  const badge = useDataMode("google_trends")



  const fetchKeywords = useCallback(

    () => api.keywords(80, filter, "google_trends", 168),

    [filter]

  )

  const { data, loading } = useApi<Keyword[]>(fetchKeywords, [], 300000)

  const cloudWords = useMemo(() => layoutWrapCloud(data), [data])



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

        <div className="w-full max-w-full rounded-xl bg-[#060608] border border-white/5 p-6 min-h-[280px]">

          <div className="flex flex-wrap gap-x-4 gap-y-3 justify-center items-center">

            {cloudWords.map((w) => (

              <span

                key={w.keyword}

                className="font-bold leading-tight select-none text-center"

                style={{

                  fontSize: `clamp(11px, ${w.fontSize}px, ${w.fontSize}px)`,

                  color: w.color,

                  opacity: 0.85 + w.weight * 0.15,

                }}

              >

                {w.keyword}

              </span>

            ))}

          </div>

        </div>

      )}

    </div>

  )

}


