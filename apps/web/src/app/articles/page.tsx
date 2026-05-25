"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, ArticleState } from "@/lib/api";
import { Plus, RefreshCw, Search } from "lucide-react";

const statusColors: Record<string, string> = {
  processing: "bg-blue-100 text-blue-800",
  review: "bg-yellow-100 text-yellow-800",
  published: "bg-green-100 text-green-800",
  approved: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
  revision: "bg-orange-100 text-orange-800",
  rejected: "bg-gray-100 text-gray-800",
};

export default function ArticlesPage() {
  const [articles, setArticles] = useState<ArticleState[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const status = statusFilter === "all" ? undefined : statusFilter;
      const res = await api.listArticles({ status, page, limit });
      setArticles(res.articles);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    load();
  }, [statusFilter, page, load]);

  const filtered = searchQuery
    ? articles.filter(
        (a) =>
          (a.raw_input || a.article_id).toLowerCase().includes(searchQuery.toLowerCase()) ||
          (a.published_title || "").toLowerCase().includes(searchQuery.toLowerCase())
      )
    : articles;

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Artikel</h1>
          <p className="text-muted-foreground">Daftar semua artikel</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={() => load()}>
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Link href="/articles/new">
            <Button>
              <Plus className="w-4 h-4 mr-1" /> Artikel Baru
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex gap-3 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Cari artikel..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v ?? "all"); setPage(1); }}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Semua Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Semua Status</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="review">Review</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="published">Published</SelectItem>
            <SelectItem value="revision">Revision</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            {total} Artikel
            {statusFilter !== "all" && ` — filter: ${statusFilter}`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Memuat...</p>
          ) : filtered.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {searchQuery
                ? "Tidak ada artikel yang cocok dengan pencarian."
                : "Belum ada artikel. Buat artikel baru untuk memulai."}
            </p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Judul / Input</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Skor</TableHead>
                    <TableHead>Tanggal</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((a) => (
                    <TableRow key={a.article_id}>
                      <TableCell className="font-medium max-w-[250px] truncate">
                        {a.raw_input || a.article_id}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={statusColors[a.status] ?? ""}>
                          {a.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {a.credibility_score !== null
                          ? `${(a.credibility_score * 100).toFixed(0)}`
                          : "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {new Date(a.created_at * 1000).toLocaleDateString("id-ID")}
                      </TableCell>
                      <TableCell>
                        <Link href={`/articles/${a.article_id}`}>
                          <Button variant="ghost" size="sm">Detail</Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <p className="text-sm text-muted-foreground">
                    Halaman {page} dari {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                    >
                      Sebelumnya
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page >= totalPages}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Selanjutnya
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
