import { useState, useCallback, useMemo } from "react"

import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps"

import { useApi } from "../hooks/useApi"

import { api } from "../api"

import type { CountryTrend } from "../types"

import { COUNTRY_CENTROIDS } from "../data/countryCentroids"

import { WC_TEAMS } from "../data/teams"

import { getFlagImageUrl } from "../data/teamFlagCodes"

import { getFlag } from "./TeamFlag"

import LoadingSkeleton from "./LoadingSkeleton"

import DataBadge from "./DataBadge"

import { useDataMode } from "../hooks/useDataMode"



const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"



const NAME_TO_ISO: Record<string, string> = {

  "United States of America": "US", "United States": "US", "Canada": "CA", "Mexico": "MX",

  "Brazil": "BR", "Argentina": "AR", "United Kingdom": "GB", "France": "FR", "Germany": "DE",

  "Spain": "ES", "Italy": "IT", "Portugal": "PT", "Netherlands": "NL", "Belgium": "BE",

  "Switzerland": "CH", "Poland": "PL", "Sweden": "SE", "Norway": "NO", "Denmark": "DK",

  "Ireland": "IE", "Austria": "AT", "Croatia": "HR", "Serbia": "RS", "Turkey": "TR",

  "Morocco": "MA", "Senegal": "SN", "Nigeria": "NG", "Cameroon": "CM", "Egypt": "EG",

  "South Africa": "ZA", "Japan": "JP", "South Korea": "KR", "China": "CN", "India": "IN",

  "Australia": "AU", "New Zealand": "NZ", "Saudi Arabia": "SA", "Iran": "IR", "Qatar": "QA",

  "Ecuador": "EC", "Colombia": "CO", "Uruguay": "UY", "Chile": "CL", "Peru": "PE",

  "Venezuela": "VE", "Greece": "GR", "Czechia": "CZ", "Czech Republic": "CZ",

  "Hungary": "HU", "Ukraine": "UA", "Russia": "RU", "Israel": "IL", "Thailand": "TH",

  "Vietnam": "VN", "Philippines": "PH", "Indonesia": "ID", "Malaysia": "MY",

  "Pakistan": "PK", "Bangladesh": "BD", "Ivory Coast": "CI", "Côte d'Ivoire": "CI",

  "Algeria": "DZ", "Ghana": "GH", "Tunisia": "TN", "Dem. Rep. Congo": "CD",

  "Democratic Republic of the Congo": "CD", "Cabo Verde": "CV", "Iraq": "IQ", "Jordan": "JO",

  "Uzbekistan": "UZ", "Haiti": "HT", "Panama": "PA", "Paraguay": "PY",

  "Bosnia and Herzegovina": "BA", "Bosnia and Herz.": "BA", "Curaçao": "CW",

}



const METHODOLOGY_GEO =
  "Only ~75 major countries are covered on this map — not all ~195 nations — because Google Trends enforces strict rate limits on regional queries."



type FlagSizeKey = "sm" | "md" | "lg"



function flagSizeKey(pixelHeight: number): FlagSizeKey {

  if (pixelHeight <= 20) return "sm"

  if (pixelHeight <= 28) return "md"

  return "lg"

}



function MapFlagImg({ team, height = 24 }: { team: string; height?: number }) {

  const src = getFlagImageUrl(team, flagSizeKey(height))

  const width = Math.round(height * 1.35)

  if (!src) {

    return <span className="text-lg leading-none">{getFlag(team)}</span>

  }

  return (

    <img

      src={src}

      alt=""

      width={width}

      height={height}

      className="rounded-sm shadow-md border border-white/20 object-cover"

    />

  )

}



function MapFlagSvg({ team, w, h }: { team: string; w: number; h: number }) {

  const src = getFlagImageUrl(team, flagSizeKey(h))

  if (!src) {

    return (

      <text textAnchor="middle" dominantBaseline="central" fontSize={h * 0.85}>

        {getFlag(team)}

      </text>

    )

  }

  return (

    <image

      href={src}

      x={-w / 2}

      y={-h / 2}

      width={w}

      height={h}

      preserveAspectRatio="xMidYMid meet"

    />

  )

}



export default function GeographicHeatmap() {

  const [highlightTeam, setHighlightTeam] = useState("")

  const [tooltip, setTooltip] = useState<CountryTrend | null>(null)

  const badge = useDataMode("google_trends")



  const fetchRegions = useCallback(

    () => api.trendRegions(highlightTeam || undefined),

    [highlightTeam]

  )

  const { data, loading } = useApi(
    fetchRegions,
    { countries: [], highlight_team: null, countries_with_data: 0, countries_total: 0 },
    3600000
  )



  const markers = useMemo(() => {

    return data.countries

      .filter((c) => c.has_regional_data && c.top_team && COUNTRY_CENTROIDS[c.code])

      .filter(

        (c) =>

          !highlightTeam ||

          c.top_team === highlightTeam ||

          (c.top5 || c.top3 || []).some((t) => t.team === highlightTeam)

      )

      .map((c) => ({

        ...c,

        coordinates: COUNTRY_CENTROIDS[c.code] as [number, number],

      }))

  }, [data.countries, highlightTeam])



  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">

      <div className="flex flex-wrap items-center justify-between gap-3">

        <div className="flex items-center gap-2">

          <h2 className="text-white font-semibold">Geographic Heatmap</h2>

          <DataBadge mode={badge} />

        </div>

        <select

          value={highlightTeam}

          onChange={(e) => setHighlightTeam(e.target.value)}

          className="bg-[#1a1a22] border border-white/20 text-white text-xs rounded-lg px-3 py-1.5 [&>option]:bg-[#1a1a22] [&>option]:text-white"

        >

          <option value="">All teams worldwide</option>

          {WC_TEAMS.map((t) => (

            <option key={t} value={t}>

              {t}

            </option>

          ))}

        </select>

      </div>



      <div className="relative group max-w-3xl">
        <p className="text-white/50 text-xs cursor-help underline decoration-dotted decoration-white/25 underline-offset-2">
          Google Trends · which WC nation is searched most in each country · Please hover for top 5 within each nation
          {data.countries_with_data != null ? (
            <> · {data.countries_with_data}/{data.countries_total} countries with regional data</>
          ) : null}
        </p>
        <div
          role="tooltip"
          className="pointer-events-none absolute left-0 top-full z-20 mt-2 w-full max-w-md rounded-lg border border-white/15 bg-[#0a0a0e] px-3 py-2.5 text-[11px] text-white/75 opacity-0 shadow-xl transition-opacity group-hover:opacity-100"
        >
          <p>{METHODOLOGY_GEO}</p>
        </div>
      </div>



      {loading ? (

        <LoadingSkeleton rows={6} />

      ) : (

        <div className="relative w-full max-w-full rounded-xl overflow-hidden border border-white/15 bg-[#0c0c10] aspect-[800/420]">

          <ComposableMap

            projection="geoEqualEarth"

            projectionConfig={{ scale: 155, center: [10, 5] }}

            width={800}

            height={420}

            style={{ width: "100%", height: "100%", display: "block" }}

          >

            <Geographies geography={GEO_URL}>

              {({ geographies }) =>

                geographies.map((geo) => {

                  const name = geo.properties?.name as string

                  const code = NAME_TO_ISO[name]

                  const hasMarker = code && markers.some((m) => m.code === code)

                  return (

                    <Geography

                      key={geo.rsmKey}

                      geography={geo}

                      style={{

                        default: {

                          fill: hasMarker ? "#243044" : "#1a2030",

                          stroke: "#4a5a72",

                          strokeWidth: 0.6,

                          outline: "none",

                        },

                        hover: {

                          fill: "#2d3a52",

                          stroke: "#6b8299",

                          strokeWidth: 0.8,

                          outline: "none",

                        },

                        pressed: { outline: "none" },

                      }}

                    />

                  )

                })

              }

            </Geographies>



            {markers.map((m) => {

              const active = !highlightTeam || m.top_team === highlightTeam

              const size = active ? 18 : 14

              return (

                <Marker

                  key={m.code}

                  coordinates={m.coordinates}

                  onMouseEnter={() => setTooltip(m)}

                  onMouseLeave={() => setTooltip(null)}

                >

                  <g opacity={active ? 1 : 0.55} style={{ cursor: "pointer" }}>

                    <circle r={size * 0.5} fill="#060608" fillOpacity={0.75} />

                    <MapFlagSvg team={m.top_team!} w={size * 1.35} h={size} />

                  </g>

                </Marker>

              )

            })}

          </ComposableMap>



          {tooltip && (

            <div className="absolute top-2 left-2 right-2 sm:top-3 sm:left-auto sm:right-3 sm:max-w-[220px] bg-[#0a0a0e]/95 border border-emerald-500/40 rounded-xl p-3 sm:p-4 text-xs z-10 shadow-2xl backdrop-blur-sm">

              <p className="text-white font-semibold text-sm border-b border-white/10 pb-2 mb-2">

                {tooltip.name}

              </p>

              <p className="text-emerald-400/90 text-[10px] uppercase tracking-wider mb-2">

                Search interest in FIFA participating nations

              </p>

              <ol className="space-y-2">

                {(tooltip.top5 || tooltip.top3 || []).slice(0, 5).map((t, i) => (

                  <li key={t.team} className="flex items-center gap-2">

                    <span className="text-white/35 w-4 font-mono">{i + 1}</span>

                    <MapFlagImg team={t.team} height={16} />

                    <span className="text-white flex-1 text-sm">{t.team}</span>

                    <span className="text-emerald-400/90 font-mono text-[11px]">{t.score}</span>

                  </li>

                ))}

              </ol>

            </div>

          )}



          <div className="absolute bottom-3 left-3 flex items-center gap-2 text-[10px] text-white/40 bg-black/60 px-2 py-1 rounded-lg border border-white/10">

            <MapFlagImg team="Brazil" height={14} />

            <span>= most-searched WC team in that country</span>

          </div>

        </div>

      )}

    </div>

  )

}


