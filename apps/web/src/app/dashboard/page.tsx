"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { api, ArticleState } from "@/lib/api";
import { ActivityChart } from "@/components/dashboard/activity-chart";
import { FileText, CheckCircle2, Clock, AlertCircle, Eye } from "lucide-react";

const statusColors: Record<string, string> = {
  processing: "bg-blue-100 text-blue-800",
  review: "bg-yellow-100 text-yellow-800",
  published: "bg-green-100 text-green-800",
  approved: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
  revision: "bg-orange-100 text-orange-800",
  rejected: "bg-gray-100 text-gray-800",
};

function groupByDate(articles: ArticleState[], days: number) {
  const groups: Record<string, { published: number; review: number; failed: number }> = {};
  const now = Date.now();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now - i * 86400000);
    const key = d.toISOString().slice(0, 10);
    groups[key] = { published: 0, review: 0, failed: 0 };
  }
  for (const a of articles) {
    const key = new Date(a.created_at * 1000).toISOString().slice(0, 10);
    if (groups[key]) {
      if (a.status === "published") groups[key].published++;
      else if (a.status === "review" || a.status === "revision") groups[key].review++;
      else if (a.status === "failed") groups[key].failed++;
    }
  }
  return Object.entries(groups).map(([date, counts]) => ({
    date,
    label: new Date(date).toLocaleDateString("id-ID", { weekday: "short", day: "numeric" }),
    ...counts,
  }));
}

export default function DashboardPage() {
  const [articles, setArticles] = useState<ArticleState[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const fetchArticles = () =>
      api.listArticles({ limit: 100 }).then(
        (res) => {
          if (!cancelled) {
            setArticles(res.articles);
            setLoading(false);
          }
        },
        () => {
          if (!cancelled) setLoading(false);
        }
      );

    fetchArticles();
    const interval = setInterval(fetchArticles, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const total = articles.length;
  const published = articles.filter((a) => a.status === "published").length;
  const review = articles.filter((a) => a.status === "review" || a.status === "revision").length;
  const failed = articles.filter((a) => a.status === "failed").length;
  const avgScore =
    articles
      .filter((a) => a.credibility_score !== null)
      .reduce((sum, a) => sum + (a.credibility_score ?? 0), 0) /
      Math.max(articles.filter((a) => a.credibility_score !== null).length, 1) || 0;

  const recentArticles = articles.slice(0, 8);
  const reviewArticles = articles.filter((a) => a.status === "review");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Ringkasan aktivitas pipeline</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <MetricCard
          icon={<FileText className="w-4 h-4" />}
          label="Total Artikel"
          value={total}
        />
        <MetricCard
          icon={<CheckCircle2 className="w-4 h-4 text-green-600" />}
          label="Published"
          value={published}
        />
        <MetricCard
          icon={<Clock className="w-4 h-4 text-yellow-600" />}
          label="Butuh Review"
          value={review}
        />
        <MetricCard
          icon={<AlertCircle className="w-4 h-4 text-red-600" />}
          label="Gagal"
          value={failed}
        />
        <MetricCard
          icon={<Eye className="w-4 h-4 text-blue-600" />}
          label="Rata-rata Skor"
          value={avgScore > 0 ? `${(avgScore * 100).toFixed(0)}` : "—"}
        />
      </div>

      {reviewArticles.length > 0 && (
        <Card className="border-yellow-300 bg-yellow-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-yellow-800">
              <Clock className="w-4 h-4" />
              Artikel Butuh Review ({reviewArticles.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {reviewArticles.slice(0, 5).map((a) => (
                <div key={a.article_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm truncate max-w-[300px]">
                      {a.raw_input || a.article_id}
                    </span>
                    {a.credibility_score !== null && (
                      <span className="text-xs text-muted-foreground">
                        ({(a.credibility_score * 100).toFixed(0)})
                      </span>
                    )}
                  </div>
                  <Link href={`/articles/${a.article_id}`}>
                    <Button variant="outline" size="sm">Review</Button>
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <ActivityChart data={groupByDate(articles, 7)} />

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Artikel Terbaru</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading ? (
              <p className="text-sm text-muted-foreground">Memuat...</p>
            ) : recentArticles.length === 0 ? (
              <p className="text-sm text-muted-foreground">Belum ada artikel</p>
            ) : (
              recentArticles.map((a) => (
                <div key={a.article_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-sm truncate max-w-[200px]">
                      {a.raw_input || a.article_id}
                    </span>
                    {a.credibility_score !== null && (
                      <span className="text-xs font-mono text-muted-foreground shrink-0">
                        {(a.credibility_score * 100).toFixed(0)}
                      </span>
                    )}
                  </div>
                  <Badge variant="outline" className={(statusColors[a.status] ?? "") + " shrink-0"}>
                    {a.status}
                  </Badge>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{label}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}
