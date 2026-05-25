"use client";

import { EventDict } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { MessageSquare, ArrowRight } from "lucide-react";

export function DebateLog({ events }: { events: EventDict[] }) {
  const debateEvents = events.filter((e) => e.agent === "Aggregator");
  if (debateEvents.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Belum ada log debat.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {debateEvents.map((e, i) => (
        <Card key={i}>
          <CardContent className="pt-4 flex items-start gap-3">
            <div className="mt-0.5">
              <MessageSquare className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <span className="font-medium">{e.agent}</span>
                <ArrowRight className="w-3 h-3" />
                <span>{e.action}</span>
                <span>&middot;</span>
                <span>{new Date(e.timestamp).toLocaleString("id-ID")}</span>
              </div>
              <p className="text-sm">{e.detail || "Tidak ada detail"}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
