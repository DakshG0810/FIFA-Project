import { useState, useCallback, useMemo } from "react"
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps"
import { useApi } from "../hooks/useApi"
import { api } from "../api"
import type { CountryTrend } from "../types"
import { COUNTRY_CENTROIDS } from "../data/countryCentroids"
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
  "Pakistan": "PK", "Bangladesh": "BD",
}

const HIGHLIGHT_TEAMS = [
  "Argentina", "France", "England", "Brazil", "Spain", "Germany", "USA", "Mexico", "Japan",
]

type FlagSizeKey = "sm" | "md" | "lg"

function flagSizeKey(pixelHeight: number): FlagSizeKey {
  if (pixelHeight <= 20) return "sm"
  if (pixelHeight <= 28) return "md"
  return "lg"
}

/** HTML tooltip / legend — img works outside SVG */
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

/** SVG map pins — use <image>, not foreignObject (broken in many browsers) */
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
  const { data, loading } = useApi(fetchRegions, { countries: [], highlight_team: null }, 3600000)

  const markers = useMemo(() => {
    return data.countries
      .filter((c) => c.top_team && COUNTRY_CENTROIDS[c.code])
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
          className="bg-[#1a1a22] border border-white/20 text-white text-xs rounded-lg px-3 py-1.5"
        >
          <option value="">All teams worldwide</option>
          {HIGHLIGHT_TEAMS.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <p className="text-white/50 text-xs">
        Each pin shows the <strong className="text-white/70">WC team flag</strong> with the most fan interest in that country. Hover for the top 5.
      </p>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : (
        <div className="relative rounded-xl overflow-hidden border border-white/15 bg-[#0c0c10]">
          <ComposableMap
            projection="geoEqualEarth"
            projectionConfig={{ scale: 155, center: [10, 5] }}
            width={800}
            height={420}
            style={{ width: "100%", height: "auto", display: "block" }}
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
              const size = active ? 32 : 22
              return (
                <Marker
                  key={m.code}
                  coordinates={m.coordinates}
                  onMouseEnter={() => setTooltip(m)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <g opacity={active ? 1 : 0.55} style={{ cursor: "pointer" }}>
                    <circle r={size * 0.55} fill="#060608" fillOpacity={0.75} />
                    <MapFlagSvg team={m.top_team!} w={size * 1.35} h={size} />
                  </g>
                </Marker>
              )
            })}
          </ComposableMap>

          {tooltip && (
            <div className="absolute top-3 right-3 bg-[#0a0a0e]/95 border border-emerald-500/40 rounded-xl p-4 text-xs max-w-[220px] z-10 shadow-2xl backdrop-blur-sm">
              <p className="text-white font-semibold text-sm border-b border-white/10 pb-2 mb-2">
                {tooltip.name}
              </p>
              <p className="text-emerald-400/90 text-[10px] uppercase tracking-wider mb-2">
                Top 5 supported teams
              </p>
              <ol className="space-y-2">
                {(tooltip.top5 || tooltip.top3 || []).slice(0, 5).map((t, i) => (
                  <li key={t.team} className="flex items-center gap-2">
                    <span className="text-white/35 w-4 font-mono">{i + 1}</span>
                    <MapFlagImg team={t.team} height={18} />
                    <span className="text-white flex-1 text-sm">{t.team}</span>
                    <span className="text-emerald-400/90 font-mono text-[11px]">{t.score}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          <div className="absolute bottom-3 left-3 flex items-center gap-2 text-[10px] text-white/40 bg-black/60 px-2 py-1 rounded-lg border border-white/10">
            <MapFlagImg team="Brazil" height={16} />
            <span>= most-searched WC team in that country</span>
          </div>
        </div>
      )}
    </div>
  )
}
