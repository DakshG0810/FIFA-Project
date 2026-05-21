export default function MomentumArrow({ momentum }: { momentum?: "up" | "down" | "flat" }) {
  if (momentum === "up") return <span className="text-emerald-400 font-mono text-xs">▲</span>
  if (momentum === "down") return <span className="text-red-400 font-mono text-xs">▼</span>
  return <span className="text-white/30 font-mono text-xs">→</span>
}
