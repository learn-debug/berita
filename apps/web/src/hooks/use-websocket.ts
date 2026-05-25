"use client";

import { useEffect, useRef, useState } from "react";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export type WsMessage =
  | { type: "connected"; article_id: string; status: string }
  | { type: "pipeline_start"; article_id: string; message: string }
  | { type: "pipeline_complete"; article_id: string; status: string }
  | { type: "pipeline_error"; article_id: string; error: string }
  | { type: "agent_start"; agent: string; timestamp: number }
  | { type: "agent_complete"; agent: string; timestamp: number }
  | { type: "agent_error"; agent: string; error: string; timestamp: number }
  | { type: "ping" };

type ConnectionState = "connecting" | "connected" | "disconnected";
type PipelineState = "idle" | "running" | "completed" | "error";

export function usePipelineWebSocket(articleId: string | null) {
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [pipelineState, setPipelineState] = useState<PipelineState>("idle");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!articleId) return;

    const ws = new WebSocket(`${WS_BASE}/ws/${articleId}`);
    wsRef.current = ws;
    setConnectionState("connecting");
    setMessages([]);
    setPipelineState("idle");

    ws.onopen = () => setConnectionState("connected");
    ws.onmessage = (msg) => {
      try {
        const data: WsMessage = JSON.parse(msg.data);
        setMessages((prev) => [...prev, data]);

        if (data.type === "pipeline_start") setPipelineState("running");
        else if (data.type === "pipeline_complete") setPipelineState("completed");
        else if (data.type === "pipeline_error") setPipelineState("error");
      } catch {
        // passthrough
      }
    };
    ws.onclose = () => {
      setConnectionState("disconnected");
      wsRef.current = null;
    };
    ws.onerror = () => {
      setConnectionState("disconnected");
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [articleId]);

  const runningAgents = new Set(
    messages
      .filter((m): m is { type: "agent_start"; agent: string } & WsMessage => m.type === "agent_start")
      .map((m) => (m as { type: "agent_start"; agent: string }).agent)
  );
  for (const m of messages) {
    if (m.type === "agent_complete" || m.type === "agent_error") {
      runningAgents.delete(m.agent);
    }
  }

  return { messages, connectionState, pipelineState, runningAgents, clear: () => setMessages([]) };
}
