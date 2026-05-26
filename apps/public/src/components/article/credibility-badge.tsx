import { cn } from "@/lib/utils"
import { ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react"

type Props = {
  score: number
  size?: "sm" | "md" | "lg"
  showLabel?: boolean
}

export function CredibilityBadge({ score, size = "md", showLabel = true }: Props) {
  const pct = Math.round(score * 100)
  const sizeClass = size === "sm" ? "gap-1 text-xs" : size === "lg" ? "gap-2 text-base" : "gap-1.5 text-sm"

  let status: { label: string; color: string; icon: typeof ShieldCheck }
  if (score >= 0.75) {
    status = { label: "Terverifikasi", color: "text-accent", icon: ShieldCheck }
  } else if (score >= 0.5) {
    status = { label: "Perlu Review", color: "text-yellow-600 dark:text-yellow-400", icon: ShieldQuestion }
  } else {
    status = { label: "Kredibilitas Rendah", color: "text-destructive", icon: ShieldAlert }
  }

  const Icon = status.icon

  return (
    <div className={cn("inline-flex items-center", sizeClass, status.color)} title={`Skor kredibilitas: ${pct}%`}>
      <Icon className={cn(size === "sm" ? "size-3.5" : size === "lg" ? "size-6" : "size-4.5")} />
      {showLabel && (
        <span className="font-medium">{status.label}</span>
      )}
      <span className={cn("font-mono font-bold", size === "sm" ? "text-[10px]" : "text-xs")}>
        {pct}%
      </span>
    </div>
  )
}
