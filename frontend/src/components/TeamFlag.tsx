const FLAGS: Record<string, string> = {
  "Argentina":   "🇦🇷", "France":      "🇫🇷", "England":     "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  "Brazil":      "🇧🇷", "Spain":       "🇪🇸", "Germany":     "🇩🇪",
  "Portugal":    "🇵🇹", "Netherlands": "🇳🇱", "USA":         "🇺🇸",
  "Mexico":      "🇲🇽", "Canada":      "🇨🇦", "Morocco":     "🇲🇦",
  "Senegal":     "🇸🇳", "Japan":       "🇯🇵", "South Korea": "🇰🇷",
  "Australia":   "🇦🇺", "Iran":        "🇮🇷", "Saudi Arabia":"🇸🇦",
  "Ecuador":     "🇪🇨", "Uruguay":     "🇺🇾", "Colombia":    "🇨🇴",
  "Switzerland": "🇨🇭", "Croatia":     "🇭🇷", "Serbia":      "🇷🇸",
  "Poland":      "🇵🇱", "Turkey":      "🇹🇷", "Nigeria":     "🇳🇬",
  "Cameroon":    "🇨🇲", "Venezuela":   "🇻🇪", "Chile":       "🇨🇱",
  "Peru":        "🇵🇪", "New Zealand": "🇳🇿",
}

export function getFlag(team: string) {
  return FLAGS[team] || "🏳"
}

export default function TeamFlag({ team, size = "md" }: { team: string; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "text-lg", md: "text-2xl", lg: "text-4xl" }
  return <span className={sizes[size]}>{getFlag(team)}</span>
}
