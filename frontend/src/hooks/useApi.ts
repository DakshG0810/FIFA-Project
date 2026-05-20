import { useState, useEffect, useCallback } from "react"

export function useApi<T>(
  fetcher: () => Promise<T>,
  defaultValue: T,
  refreshMs?: number
) {
  const [data, setData]       = useState<T>(defaultValue)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const load = useCallback(async () => {
    try {
      const result = await fetcher()
      setData(result)
      setLastUpdated(new Date())
    } catch {
      // keep previous data on error
    } finally {
      setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    load()
    if (refreshMs) {
      const id = setInterval(load, refreshMs)
      return () => clearInterval(id)
    }
  }, [load, refreshMs])

  return { data, loading, lastUpdated, refresh: load }
}
