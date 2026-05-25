"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Clock,
} from "lucide-react";

export type AgentStatus = "idle" | "running" | "completed" | "error";

const statusConfig: Record<
  AgentStatus,
  { icon: React.ReactNode; label: string; cardClass: string }
> = {
  idle: {
    icon: <Clock className="w-4 h-4 text-gray-400" />,
    label: "Menunggu",
    cardClass: "border-gray-200",
  },
  running: {
    icon: <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />,
    label: "Berjalan",
    cardClass: "border-blue-300 bg-blue-50/50",
  },
  completed: {
    icon: <CheckCircle2 className="w-4 h-4 text-green-600" />,
    label: "Selesai",
    cardClass: "border-green-200",
  },
  error: {
    icon: <AlertCircle className="w-4 h-4 text-red-600" />,
    label: "Error",
    cardClass: "border-red-300 bg-red-50/50",
  },
};

export function AgentStatusCard({
  name,
  status,
  detail,
}: {
  name: string;
  status: AgentStatus;
  detail?: string;
}) {
  const cfg = statusConfig[status];
  return (
    <Card className={cn("transition-colors", cfg.cardClass)}>
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">{name}</CardTitle>
        <div className="flex items-center gap-1.5">
          {cfg.icon}
          <span
            className={cn(
              "text-xs font-medium",
              status === "running" && "text-blue-700",
              status === "completed" && "text-green-700",
              status === "error" && "text-red-700",
              status === "idle" && "text-gray-500"
            )}
          >
            {cfg.label}
          </span>
        </div>
      </CardHeader>
      {detail && (
        <CardContent className="pt-0">
          <p className="text-xs text-muted-foreground truncate">{detail}</p>
        </CardContent>
      )}
    </Card>
  );
}
