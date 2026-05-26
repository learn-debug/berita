"use client"

import { useState, useId } from "react"
import { cn } from "@/lib/utils"
import { CheckCircle2, XCircle, HelpCircle, ExternalLink } from "lucide-react"
import type { Claim } from "@/lib/api"

type Props = {
  claim: Claim
}

const verdictConfig = {
  verified: { label: "Terverifikasi", color: "text-accent", bg: "bg-accent/10", border: "border-accent/30", icon: CheckCircle2 },
  false: { label: "Tidak Terverifikasi", color: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/30", icon: XCircle },
  unverified: { label: "Tidak Dapat Diverifikasi", color: "text-muted-foreground", bg: "bg-muted", border: "border-border", icon: HelpCircle },
}

export function FactClaimTooltip({ claim }: Props) {
  const [open, setOpen] = useState(false)
  const id = useId()
  const config = verdictConfig[claim.verdict] || verdictConfig.unverified
  const Icon = config.icon

  return (
    <span className="relative inline">
      <button
        onClick={() => setOpen(!open)}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className={cn(
          "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium cursor-pointer border transition-colors",
          config.bg,
          config.border,
          config.color,
        )}
        aria-describedby={id}
        type="button"
      >
        <Icon className="size-3" />
        <span>Klaim</span>
      </button>
      {open && (
        <div
          id={id}
          role="tooltip"
          className={cn(
            "absolute z-50 mt-1 w-80 p-3 rounded-lg shadow-lg border text-sm",
            "bg-card text-card-foreground border-border",
            "left-0",
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <Icon className={cn("size-4", config.color)} />
            <span className={cn("font-semibold text-xs uppercase tracking-wide", config.color)}>
              {config.label}
            </span>
          </div>
          <p className="text-sm mb-2 leading-relaxed">&ldquo;{claim.claim}&rdquo;</p>
          {claim.evidence && (
            <div className="flex items-start gap-1.5 text-xs text-muted-foreground">
              <ExternalLink className="size-3 mt-0.5 shrink-0" />
              <span>{claim.evidence}</span>
            </div>
          )}
          {claim.trust_score !== undefined && (
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                <div
                  className={cn("h-full rounded-full transition-all", claim.trust_score >= 0.7 ? "bg-accent" : claim.trust_score >= 0.4 ? "bg-yellow-400" : "bg-destructive")}
                  style={{ width: `${claim.trust_score * 100}%` }}
                />
              </div>
              <span className="text-[10px] font-mono text-muted-foreground">
                {Math.round(claim.trust_score * 100)}%
              </span>
            </div>
          )}
        </div>
      )}
    </span>
  )
}
