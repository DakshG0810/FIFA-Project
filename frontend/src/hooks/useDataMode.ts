import { useCallback } from "react"
import { useApi } from "./useApi"
import { api } from "../api"
import type { ApiStatus, DataMode } from "../types"

function toBadge(mode: string | undefined): DataMode {
  if (mode === "live" || mode === "live_capable") return "LIVE"
  if (mode === "demo" || mode === "demo_fallback") return "DEMO"
  if (mode === "cached") return "CACHED"
  return "CACHED"
}

export function useDataMode(source: "bluesky" | "google_trends" | "odds") {
  const fetchStatus = useCallback(() => api.status(), [])
  const { data: status } = useApi<ApiStatus>(fetchStatus, {
    status: "offline",
    total_snapshots: 0,
    server_time: "",
    data_sources: {},
  }, 30_000)

  const raw = status?.data_sources?.[source]
  return toBadge(raw)
}

export function useAllDataModes() {
  const fetchStatus = useCallback(() => api.status(), [])
  return useApi<ApiStatus>(fetchStatus, {
    status: "offline",
    total_snapshots: 0,
    server_time: "",
    data_sources: {},
  }, 30_000)
}
