"use client";

import { FactCheckReport as FactCheckReportType, VerdictRaw } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ShieldCheck, ShieldAlert, ShieldQuestion, FileSearch, Search, BookOpen, Scale } from "lucide-react";

const putusanColors: Record<string, string> = {
  SUPPORTED: "bg-green-100 text-green-800 border-green-200",
  REFUTED: "bg-red-100 text-red-800 border-red-200",
  NOT_ENOUGH_EVIDENCE: "bg-yellow-100 text-yellow-800 border-yellow-200",
};

const putusanIcon: Record<string, React.ReactNode> = {
  SUPPORTED: <ShieldCheck className="w-4 h-4 text-green-600" />,
  REFUTED: <ShieldAlert className="w-4 h-4 text-red-600" />,
  NOT_ENOUGH_EVIDENCE: <ShieldQuestion className="w-4 h-4 text-yellow-600" />,
};

const keyakinanColors: Record<string, string> = {
  TINGGI: "bg-green-100 text-green-700",
  SEDANG: "bg-yellow-100 text-yellow-700",
  RENDAH: "bg-red-100 text-red-700",
};

function VerdictItem({ v }: { v: VerdictRaw }) {
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className="font-medium text-sm flex items-center gap-2">
            {putusanIcon[v.putusan]}
            {v.claim}
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          <Badge variant="outline" className={putusanColors[v.putusan]}>
            {v.putusan === "SUPPORTED"
              ? "Didukung"
              : v.putusan === "REFUTED"
                ? "Terbantahkan"
                : "Tidak Cukup Bukti"}
          </Badge>
          <Badge variant="outline" className={keyakinanColors[v.keyakinan]}>
            {v.keyakinan === "TINGGI"
              ? "Tinggi"
              : v.keyakinan === "SEDANG"
                ? "Sedang"
                : "Rendah"}
          </Badge>
        </div>
      </div>

      <div className="grid gap-2 text-sm">
        <div>
          <span className="text-xs font-medium text-muted-foreground">Premis Fakta:</span>
          <p className="text-muted-foreground">{v.premis_fakta}</p>
        </div>
        <div>
          <span className="text-xs font-medium text-muted-foreground">Premis Bukti:</span>
          <p className="text-muted-foreground">{v.premis_bukti}</p>
        </div>
        <div>
          <span className="text-xs font-medium text-muted-foreground">Premis Sumber:</span>
          <p className="text-muted-foreground">{v.premis_sumber}</p>
        </div>
        <div>
          <span className="text-xs font-medium text-muted-foreground">Analisis:</span>
          <p className="text-muted-foreground">{v.analisis}</p>
        </div>
        <div>
          <span className="text-xs font-medium text-muted-foreground">Alasan:</span>
          <p className="text-muted-foreground">{v.alasan}</p>
        </div>
      </div>
    </div>
  );
}

export function FactCheckReportView({ report }: { report?: FactCheckReportType }) {
  if (!report) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">Belum ada laporan fact-check.</p>
        </CardContent>
      </Card>
    );
  }

  const verdicts = report.verdict_raw ?? [];
  const supported = verdicts.filter((v) => v.putusan === "SUPPORTED").length;
  const refuted = verdicts.filter((v) => v.putusan === "REFUTED").length;
  const unclear = verdicts.filter((v) => v.putusan === "NOT_ENOUGH_EVIDENCE").length;

  return (
    <div className="space-y-4">
      {verdicts.length > 0 && (
        <div className="flex gap-3">
          <Card className="flex-1">
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold text-green-600">{supported}</p>
              <p className="text-xs text-muted-foreground">Didukung</p>
            </CardContent>
          </Card>
          <Card className="flex-1">
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold text-red-600">{refuted}</p>
              <p className="text-xs text-muted-foreground">Terbantahkan</p>
            </CardContent>
          </Card>
          <Card className="flex-1">
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold text-yellow-600">{unclear}</p>
              <p className="text-xs text-muted-foreground">Tak Jelas</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="verdicts">
        <TabsList>
          <TabsTrigger value="verdicts" className="flex items-center gap-1">
            <Scale className="w-3 h-3" /> Putusan
          </TabsTrigger>
          <TabsTrigger value="claims" className="flex items-center gap-1">
            <FileSearch className="w-3 h-3" /> Klaim
          </TabsTrigger>
          <TabsTrigger value="queries" className="flex items-center gap-1">
            <Search className="w-3 h-3" /> Query
          </TabsTrigger>
          <TabsTrigger value="evidence" className="flex items-center gap-1">
            <BookOpen className="w-3 h-3" /> Bukti
          </TabsTrigger>
        </TabsList>

        <TabsContent value="verdicts" className="space-y-3">
          {verdicts.length > 0 ? (
            <ScrollArea className="max-h-96">
              <div className="space-y-3">
                {verdicts.map((v, i) => (
                  <VerdictItem key={i} v={v} />
                ))}
              </div>
            </ScrollArea>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Belum ada putusan.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="claims">
          <Card>
            <CardContent className="pt-4">
              <pre className="text-sm whitespace-pre-wrap">{report.claims || "Tidak ada data."}</pre>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queries">
          <Card>
            <CardContent className="pt-4">
              <pre className="text-sm whitespace-pre-wrap">{report.queries || "Tidak ada data."}</pre>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="evidence">
          <Card>
            <CardContent className="pt-4">
              <ScrollArea className="max-h-96">
                <pre className="text-sm whitespace-pre-wrap">{report.evidence || "Tidak ada data."}</pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
