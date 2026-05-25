"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Send, Loader2 } from "lucide-react";

export default function NewArticlePage() {
  const router = useRouter();
  const [inputType, setInputType] = useState("topic");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!content.trim()) {
      toast.error("Konten harus diisi");
      return;
    }
    setLoading(true);
    try {
      const result = await api.processArticle(inputType, content);
      toast.success("Artikel dikirim ke pipeline");
      router.push(`/articles/${result.article_id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Gagal memproses");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Artikel Baru</h1>
        <p className="text-muted-foreground">Kirim topik atau draf ke pipeline</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Detail Input</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Tipe Input</label>
            <Select value={inputType} onValueChange={(v) => v && setInputType(v)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="topic">Topik</SelectItem>
                <SelectItem value="draft">Draf Mentah</SelectItem>
                <SelectItem value="url">URL Sumber</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              {inputType === "topic"
                ? "Topik Artikel"
                : inputType === "draft"
                ? "Teks Draf"
                : "URL Sumber"}
            </label>
            {inputType === "draft" ? (
              <Textarea
                placeholder="Tulis draf artikel di sini..."
                rows={10}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            ) : (
              <Input
                placeholder={
                  inputType === "topic"
                    ? "Contoh: Dampak AI terhadap industri media Indonesia"
                    : "https://..."
                }
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            )}
          </div>

          <Button
            className="w-full"
            onClick={handleSubmit}
            disabled={loading || !content.trim()}
          >
            {loading ? (
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
            ) : (
              <Send className="w-4 h-4 mr-1" />
            )}
            Kirim ke Pipeline
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
