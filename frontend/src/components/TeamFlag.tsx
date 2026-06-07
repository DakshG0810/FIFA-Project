import { getFlagImageUrl, type FlagSize } from "../data/teamFlagCodes"

const SIZE_MAP: Record<"sm" | "md" | "lg", { flag: FlagSize; w: number; h: number }> = {
  sm: { flag: "sm", w: 27, h: 20 },
  md: { flag: "md", w: 43, h: 32 },
  lg: { flag: "lg", w: 54, h: 40 },
}

export default function TeamFlag({ team, size = "md" }: { team: string; size?: "sm" | "md" | "lg" }) {
  const { flag, w, h } = SIZE_MAP[size]
  const src = getFlagImageUrl(team, flag)
  if (!src) {
    return <span className="inline-block w-5 h-4 rounded-sm bg-white/10 shrink-0" aria-hidden />
  }
  return (
    <img
      src={src}
      alt=""
      width={w}
      height={h}
      className="rounded-sm border border-white/15 object-cover shrink-0 inline-block"
    />
  )
}

/** @deprecated Prefer <TeamFlag /> — emoji flags render as 2-letter codes on Windows */
export function getFlag(_team: string) {
  return ""
}
