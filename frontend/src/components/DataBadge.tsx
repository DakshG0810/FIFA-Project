import type { DataMode } from "../types"
export type { DataMode }

export default function DataBadge({ mode }: { mode: DataMode }) {
  const styles: Record<DataMode, string> = {
    LIVE: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    CACHED: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    DEMO: "bg-sky-500/20 text-sky-400 border-sky-500/30",
  }
  return (
    <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border ${styles[mode]}`}>
      {mode}
    </span>
  )
}
