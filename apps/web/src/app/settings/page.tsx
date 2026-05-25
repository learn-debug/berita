"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Save, Sliders, Shield, GitMerge, Globe, Bell } from "lucide-react";

export default function SettingsPage() {
  const [threshold, setThreshold] = useState("0.75");
  const [midThreshold, setMidThreshold] = useState("0.50");
  const [maxClaims, setMaxClaims] = useState("5");
  const [minSourceCred, setMinSourceCred] = useState("0.3");
  const [debateRounds, setDebateRounds] = useState("2");
  const [consensusThreshold, setConsensusThreshold] = useState("0.7");
  const [cmsUrl, setCmsUrl] = useState("");
  const [publishSchedule, setPublishSchedule] = useState("immediate");

  const handleSave = (section: string) => {
    toast.success(`Pengaturan ${section} disimpan (lokal)`);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Pengaturan</h1>
        <p className="text-muted-foreground">Konfigurasi parameter sistem</p>
      </div>

      <Tabs defaultValue="quality">
        <TabsList>
          <TabsTrigger value="quality" className="flex items-center gap-1">
            <Shield className="w-3 h-3" /> Quality Gate
          </TabsTrigger>
          <TabsTrigger value="factcheck" className="flex items-center gap-1">
            <Sliders className="w-3 h-3" /> Fact-Check
          </TabsTrigger>
          <TabsTrigger value="aggregator" className="flex items-center gap-1">
            <GitMerge className="w-3 h-3" /> Aggregator
          </TabsTrigger>
          <TabsTrigger value="publisher" className="flex items-center gap-1">
            <Globe className="w-3 h-3" /> Publisher
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-1">
            <Bell className="w-3 h-3" /> Notifikasi
          </TabsTrigger>
        </TabsList>

        <TabsContent value="quality" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Threshold Credibility Score</CardTitle>
              <CardDescription>
                Menentukan routing artikel berdasarkan credibility score
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="threshold">Auto-publish threshold (&ge;)</Label>
                <Input
                  id="threshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Artikel dengan skor &ge; {threshold} akan langsung dipublikasikan
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="midThreshold">Editor review threshold (&ge;)</Label>
                <Input
                  id="midThreshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={midThreshold}
                  onChange={(e) => setMidThreshold(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Artikel dengan skor {midThreshold}–{threshold} masuk review manual
                </p>
              </div>
              <Button onClick={() => handleSave("Quality Gate")}>
                <Save className="w-4 h-4 mr-1" /> Simpan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="factcheck" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Parameter Fact-Check</CardTitle>
              <CardDescription>
                Konfigurasi jumlah sumber dan threshold kredibilitas
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="maxClaims">Jumlah sumber maksimum per klaim</Label>
                <Input
                  id="maxClaims"
                  type="number"
                  min="1"
                  max="20"
                  value={maxClaims}
                  onChange={(e) => setMaxClaims(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="minSourceCred">Threshold kredibilitas sumber</Label>
                <Input
                  id="minSourceCred"
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={minSourceCred}
                  onChange={(e) => setMinSourceCred(e.target.value)}
                />
              </div>
              <Button onClick={() => handleSave("Fact-Check")}>
                <Save className="w-4 h-4 mr-1" /> Simpan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="aggregator" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Konfigurasi Debat Aggregator</CardTitle>
              <CardDescription>
                Parameter ronde debat Delphi antar agen
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="debateRounds">Jumlah ronde debat maksimum</Label>
                <Input
                  id="debateRounds"
                  type="number"
                  min="1"
                  max="10"
                  value={debateRounds}
                  onChange={(e) => setDebateRounds(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="consensusThreshold">Threshold konsensus</Label>
                <Input
                  id="consensusThreshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={consensusThreshold}
                  onChange={(e) => setConsensusThreshold(e.target.value)}
                />
              </div>
              <Button onClick={() => handleSave("Aggregator")}>
                <Save className="w-4 h-4 mr-1" /> Simpan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="publisher" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Koneksi CMS</CardTitle>
              <CardDescription>
                Konfigurasi koneksi ke WordPress atau headless CMS
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cmsUrl">URL CMS</Label>
                <Input
                  id="cmsUrl"
                  type="url"
                  placeholder="https://cms.example.com"
                  value={cmsUrl}
                  onChange={(e) => setCmsUrl(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="publishSchedule">Jadwal publikasi default</Label>
                <select
                  id="publishSchedule"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={publishSchedule}
                  onChange={(e) => setPublishSchedule(e.target.value)}
                >
                  <option value="immediate">Langsung</option>
                  <option value="scheduled">Terjadwal</option>
                  <option value="manual">Manual</option>
                </select>
              </div>
              <Button onClick={() => handleSave("Publisher")}>
                <Save className="w-4 h-4 mr-1" /> Simpan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Notifikasi</CardTitle>
              <CardDescription>
                Konfigurasi alert untuk artikel gagal atau butuh review
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="notifEmail">Email notifikasi</Label>
                <Input
                  id="notifEmail"
                  type="email"
                  placeholder="editor@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="notifSlack">Slack Webhook URL</Label>
                <Input
                  id="notifSlack"
                  type="url"
                  placeholder="https://hooks.slack.com/..."
                />
              </div>
              <Button onClick={() => handleSave("Notifikasi")}>
                <Save className="w-4 h-4 mr-1" /> Simpan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
