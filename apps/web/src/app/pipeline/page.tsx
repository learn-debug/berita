"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { usePipelineWebSocket, WsMessage } from "@/hooks/use-websocket";
import { AgentStatusCard, AgentStatus } from "@/components/pipeline/agent-status-card";
import { Activity, Wifi, WifiOff, Play, Square } from "lucide-react";

const agentNames = [
  "orchestrator",
  "rag_pipeline",
  "draft_agent",
  "input_ingestion",
  "query_generation",
  "evidence_retrieval",
  "verdict_prediction",
  "editor_agent",
  "aggregator",
  "quality_gate",
  "publisher",
];

const agentLabels: Record<string, string> = {
  orchestrator: "Orchestrator",
  rag_pipeline: "RAG Pipeline",
  draft_agent: "Draft Agent",
  input_ingestion: "Input Ingestion",
  query_generation: "Query Generation",
  evidence_retrieval: "Evidence Retrieval",
  verdict_prediction: "Verdict Prediction",
  editor_agent: "Editor Agent",
  aggregator: "Aggregator",
  quality_gate: "Quality Gate",
  publisher: "Publisher",
};

function getAgentStatus(name: string, msgs: WsMessage[], running: Set<string>): AgentStatus {
  const agentMsgs = msgs.filter((m) => "agent" in m && m.agent === name);
  if (agentMsgs.length === 0) return "idle";
  const last = agentMsgs[agentMsgs.length - 1];
  if (running.has(name)) return "running";
  if (last.type === "agent_error") return "error";
  return "completed";
}

function getAgentDetail(name: string, msgs: WsMessage[]): string | undefined {
  const agentMsgs = msgs.filter((m) => "agent" in m && m.agent === name);
  if (agentMsgs.length === 0) return undefined;
  const last = agentMsgs[agentMsgs.length - 1];
  if (last.type === "agent_error") return last.error;
  if (last.type === "agent_complete") return `Selesai (${new Date(last.timestamp * 1000).toLocaleTimeString("id-ID")})`;
  if (last.type === "agent_start") return `Mulai (${new Date(last.timestamp * 1000).toLocaleTimeString("id-ID")})`;
  return undefined;
}

export default function PipelinePage() {
  const [articleId, setArticleId] = useState("");
  const [connected, setConnected] = useState(false);
  const { messages, connectionState, pipelineState, runningAgents, clear } =
    usePipelineWebSocket(connected ? articleId : null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Pipeline</h1>
        <p className="text-muted-foreground">Pantau status agen real-time</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Koneksi</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Input
            placeholder="article_id (contoh: art_abc123)"
            value={articleId}
            onChange={(e) => setArticleId(e.target.value)}
          />
          <Button
            variant={connected ? "destructive" : "default"}
            onClick={() => {
              if (connected) {
                setConnected(false);
                clear();
              } else {
                setConnected(true);
              }
            }}
            disabled={!articleId}
          >
            {connected ? <><Square className="w-4 h-4 mr-1" /> Putus</> : <><Play className="w-4 h-4 mr-1" /> Hubungkan</>}
          </Button>
        </CardContent>
        {connectionState === "connected" && (
          <CardContent className="pt-0 flex items-center gap-2">
            <Badge variant="outline" className="text-green-600">
              <Wifi className="w-3 h-3 mr-1" /> live
            </Badge>
            <Badge
              variant="outline"
              className={
                pipelineState === "running"
                  ? "text-blue-600"
                  : pipelineState === "completed"
                    ? "text-green-600"
                    : pipelineState === "error"
                      ? "text-red-600"
                      : "text-gray-400"
              }
            >
              {pipelineState}
            </Badge>
          </CardContent>
        )}
      </Card>

      {connected && (
        <>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {agentNames.map((name) => (
              <AgentStatusCard
                key={name}
                name={agentLabels[name]}
                status={getAgentStatus(name, messages, runningAgents)}
                detail={getAgentDetail(name, messages)}
              />
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Event Log
                {connectionState === "connected" && (
                  <Badge variant="outline" className="text-green-600 ml-auto">
                    <Wifi className="w-3 h-3 mr-1" /> live
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1 max-h-80 overflow-y-auto font-mono text-xs">
                {messages.length === 0 && (
                  <p className="text-muted-foreground">
                    Belum ada event. Hubungkan ke article_id untuk melihat log.
                  </p>
                )}
                {messages.map((m, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-muted-foreground shrink-0">
                      {"timestamp" in m
                        ? new Date((m as { timestamp: number }).timestamp * 1000).toLocaleTimeString("id-ID")
                        : ""}
                    </span>
                    <span className="font-medium shrink-0">
                      {"agent" in m ? agentLabels[m.agent as string] ?? m.agent : m.type}
                    </span>
                    <span className="text-muted-foreground">→</span>
                    <span>{m.type}</span>
                    {"error" in m && (
                      <span className="text-red-500 truncate">{m.error}</span>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
