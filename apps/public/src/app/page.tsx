import { api } from "@/lib/api"
import { ArticleCard } from "@/components/home/article-card"
import { TrendingUp, ShieldCheck, Newspaper, BarChart3 } from "lucide-react"

export const dynamic = "force-dynamic"
export const revalidate = 0

export default async function HomePage() {
  const [{ articles, total }, { categories }, stats] = await Promise.all([
    api.articles.list({ limit: 12, sort: "latest" }),
    api.categories.list(),
    api.stats.get(),
  ])

  const featured = articles[0]
  const rest = articles.slice(1, 7)

  return (
    <div>
      <section className="border-b border-border bg-gradient-to-b from-primary/5 to-background">
        <div className="container py-12 md:py-16">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
            Berita Terverifikasi AI
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Setiap artikel diproses oleh 12 agen AI untuk memastikan akurasi faktual,
            kemudian diberi skor kredibilitas secara transparan.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            <div className="flex items-center gap-3 rounded-lg bg-card border border-border p-4">
              <Newspaper className="size-8 text-primary" />
              <div>
                <div className="text-2xl font-bold">{stats.total_articles}</div>
                <div className="text-xs text-muted-foreground">Artikel</div>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-card border border-border p-4">
              <ShieldCheck className="size-8 text-accent" />
              <div>
                <div className="text-2xl font-bold">{Math.round(stats.avg_credibility_score * 100)}%</div>
                <div className="text-xs text-muted-foreground">Rata-rata Skor</div>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-card border border-border p-4">
              <TrendingUp className="size-8 text-primary" />
              <div>
                <div className="text-2xl font-bold">{categories.length}</div>
                <div className="text-xs text-muted-foreground">Kategori</div>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg bg-card border border-border p-4">
              <BarChart3 className="size-8 text-accent" />
              <div>
                <div className="text-2xl font-bold">{total}</div>
                <div className="text-xs text-muted-foreground">Total Tayang</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container py-8 md:py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Artikel Terbaru</h2>
        </div>

        {articles.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <Newspaper className="size-12 mx-auto mb-3 opacity-40" />
            <p className="text-lg">Belum ada artikel yang diterbitkan.</p>
            <p className="text-sm">Artikel akan muncul di sini setelah pipeline selesai memproses.</p>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2">
            {featured && <ArticleCard article={featured} featured />}
            {rest.map((a) => (
              <ArticleCard key={a.article_id} article={a} />
            ))}
          </div>
        )}
      </section>

      {categories.length > 1 && (
        <section className="container pb-12">
          <h2 className="text-xl font-semibold mb-6">Jelajahi Kategori</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categories.map((cat) => (
              <a
                key={cat.slug}
                href={`/kategori/${cat.slug}`}
                className="group block rounded-xl border border-border bg-card p-5 no-underline transition-all hover:shadow-md hover:border-primary/30"
              >
                <div className="text-lg font-medium text-card-foreground group-hover:text-primary transition-colors">
                  {cat.name}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {cat.count} artikel
                </div>
              </a>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
