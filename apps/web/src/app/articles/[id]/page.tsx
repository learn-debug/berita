"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { api, ArticleState } from "@/lib/api";
import { usePipelineWebSocket, WsMessage } from "@/hooks/use-websocket";
import { CredibilityGaugeCard } from "@/components/shared/credibility-gauge";
import { FactCheckReportView } from "@/components/articles/fact-check-report";
import { DebateLog } from "@/components/articles/debate-log";
import { AgentStatusCard, AgentStatus } from "@/components/pipeline/agent-status-card";
import { toast } from "sonner";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Activity,
  Wifi,
  WifiOff,
  MessageSquare,
  FileText,
  ScrollText,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const statusColors: Record<string, string> = {
  processing: "bg-blue-100 text-blue-800",
  review: "bg-yellow-100 text-yellow-800",
  published: "bg-green-100 text-green-800",
  approved: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
  revision: "bg-orange-100 text-orange-800",
  rejected: "bg-gray-100 text-gray-800",
};

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
  if (running.has(name)) return "running";
  const last = agentMsgs[agentMsgs.length - 1];
  if (last.type === "agent_error") return "error";
  return "completed";
}

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const articleId = params.id as string;
  const [article, setArticle] = useState<ArticleState | null>(null);
  const [loading, setLoading] = useState(true);
  const { messages, connectionState, pipelineState, runningAgents } = usePipelineWebSocket(articleId);

  const load = () => {
    setLoading(true);
    api.getArticle(articleId).then((res) => {
      setArticle(res);
      setLoading(false);
    });
  };

  useEffect(() => {
    load();
  }, [articleId]);

  const handleAction = async (action: string) => {
    try {
      await api.patchArticle(articleId, action);
      toast.success(
        action === "approve"
          ? "Artikel disetujui"
          : action === "reject"
            ? "Artikel ditolak"
            : "Artikel dikirim ulang"
      );
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Gagal");
    }
  };

  if (loading) {
    return <p className="text-muted-foreground">Memuat...</p>;
  }

  if (!article) {
    return <p className="text-muted-foreground">Artikel tidak ditemukan</p>;
  }

  const isProcessing = article.status === "processing";

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/articles")}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold tracking-tight truncate">
            {article.raw_input || article.article_id}
          </h1>
          <p className="text-muted-foreground text-sm">
            ID: {article.article_id} &middot; Dibuat{" "}
            {new Date(article.created_at * 1000).toLocaleString("id-ID")}
            {article.revision_count > 0 && ` &middot; Revisi ${article.revision_count}`}
          </p>
        </div>
        <Badge variant="outline" className={statusColors[article.status] ?? ""}>
          {article.status}
        </Badge>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Tabs defaultValue="article">
            <TabsList>
              <TabsTrigger value="article" className="flex items-center gap-1">
                <FileText className="w-3 h-3" /> Artikel
              </TabsTrigger>
              <TabsTrigger value="factcheck" className="flex items-center gap-1">
                <ScrollText className="w-3 h-3" /> Fact-Check
              </TabsTrigger>
              <TabsTrigger value="debate" className="flex items-center gap-1">
                <MessageSquare className="w-3 h-3" /> Debat
              </TabsTrigger>
              <TabsTrigger value="pipeline" className="flex items-center gap-1">
                <Activity className="w-3 h-3" /> Pipeline
              </TabsTrigger>
            </TabsList>

            <TabsContent value="article" className="space-y-4">
              <Card>
                <CardContent className="pt-6">
                  {article.aggregated_article || article.edited_draft || article.draft ? (
                    <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                      {article.aggregated_article || article.edited_draft || article.draft}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">Konten belum tersedia.</p>
                  )}
                </CardContent>
              </Card>

              {article.status === "review" && (
                <div className="flex gap-2">
                  <Dialog>
                    <DialogTrigger
                      render={
                        <Button className="bg-green-600 hover:bg-green-700">
                          <CheckCircle2 className="w-4 h-4 mr-1" /> Setujui & Publikasikan
                        </Button>
                      }
                    />
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Setujui Artikel</DialogTitle>
                        <DialogDescription>
                          Artikel akan dikirim ke Publisher Agent untuk ditayangkan.
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => {}}>
                          Batal
                        </Button>
                        <Button
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => handleAction("approve")}
                        >
                          Ya, Publikasikan
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>

                  <Button variant="destructive" onClick={() => handleAction("reject")}>
                    <XCircle className="w-4 h-4 mr-1" /> Tolak
                  </Button>

                  <Button variant="outline" onClick={() => handleAction("retry")}>
                    <RotateCcw className="w-4 h-4 mr-1" /> Kirim Ulang
                  </Button>
                </div>
              )}
            </TabsContent>

            <TabsContent value="factcheck">
              <FactCheckReportView report={article.fact_check_report} />
            </TabsContent>

            <TabsContent value="debate">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Log Debat Aggregator</CardTitle>
                </CardHeader>
                <CardContent>
                  <DebateLog events={article.events} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="pipeline">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Event Pipeline
                    {connectionState === "connected" ? (
                      <Badge variant="outline" className="text-green-600 ml-auto">
                        <Wifi className="w-3 h-3 mr-1" /> live
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-gray-400 ml-auto">
                        <WifiOff className="w-3 h-3 mr-1" /> disconnected
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1 max-h-80 overflow-y-auto font-mono text-xs">
                    {messages.length === 0 && article.events.length === 0 && (
                      <p className="text-muted-foreground">Belum ada event.</p>
                    )}
                    {article.events.map((e, i) => (
                      <div key={`evt-${i}`} className="flex gap-2">
                        <span className="text-muted-foreground shrink-0">
                          {new Date(e.timestamp).toLocaleTimeString("id-ID")}
                        </span>
                        <span className="font-medium shrink-0">{e.agent}</span>
                        <span className="text-muted-foreground">→</span>
                        <span>{e.action}</span>
                        {e.detail && (
                          <span className="text-muted-foreground truncate">{e.detail}</span>
                        )}
                      </div>
                    ))}
                    {messages.map((m, i) => (
                      <div key={`ws-${i}`} className="flex gap-2 text-blue-600">
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
                        {"error" in m && <span className="text-red-500 truncate">{m.error}</span>}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-4">
          <CredibilityGaugeCard score={article.credibility_score} />

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Info Artikel</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tipe Input</span>
                <span>{article.input_type}</span>
              </div>
              <Separator />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <Badge variant="outline" className={statusColors[article.status] ?? ""}>
                  {article.status}
                </Badge>
              </div>
              <Separator />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Revisi</span>
                <span>{article.revision_count}</span>
              </div>
              <Separator />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Event Agen</span>
                <span>{article.events.length}</span>
              </div>
              {article.published_url && (
                <>
                  <Separator />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">URL Publikasi</span>
                    <a
                      href={article.published_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline truncate max-w-[150px]"
                    >
                      {article.published_url}
                    </a>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {isProcessing && (
            <Card className="border-blue-300">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Pipeline Live</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {["orchestrator", "rag_pipeline", "draft_agent", "editor_agent", "aggregator", "quality_gate", "publisher"].map(
                  (name) => (
                    <AgentStatusCard
                      key={name}
                      name={agentLabels[name]}
                      status={getAgentStatus(name, messages, runningAgents)}
                    />
                  )
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
