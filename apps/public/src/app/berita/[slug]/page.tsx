import { notFound } from "next/navigation"
import { api } from "@/lib/api"
import { CredibilityBadge } from "@/components/article/credibility-badge"
import { FactClaimTooltip } from "@/components/article/fact-claim-tooltip"
import { Calendar, BookOpen, ExternalLink, RefreshCw } from "lucide-react"
import { formatDate } from "@/lib/utils"
import type { Metadata } from "next"

type Props = { params: Promise<{ slug: string }> }

async function getArticle(slug: string) {
  try {
    return await api.articles.get(slug)
  } catch {
    return null
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const article = await getArticle(slug)
  if (!article) return { title: "Artikel Tidak Ditemukan" }

  return {
    title: article.title,
    description: article.excerpt,
    openGraph: {
      title: article.title,
      description: article.excerpt,
      type: "article",
      publishedTime: article.created_at ?? undefined,
    },
  }
}

export const dynamic = "force-dynamic"
export const revalidate = 0

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params
  const article = await getArticle(slug)
  if (!article) notFound()

  const score = article.credibility_score
  const wordCount = article.body.split(" ").length

  return (
    <article className="container py-8 md:py-12">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium text-xs">
              {article.category}
            </span>
            {article.created_at && (
              <span className="inline-flex items-center gap-1">
                <Calendar className="size-3.5" />
                {formatDate(article.created_at)}
              </span>
            )}
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight leading-tight mb-4">
            {article.title}
          </h1>
          <div className="flex flex-wrap items-center gap-4">
            <CredibilityBadge score={score} size="lg" />
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
              <BookOpen className="size-4" />
              {wordCount} kata
            </span>
            {article.revision_count > 0 && (
              <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
                <RefreshCw className="size-4" />
                {article.revision_count}× revisi
              </span>
            )}
            {article.source_url && (
              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-sm no-underline hover:underline"
              >
                <ExternalLink className="size-4" />
                Sumber
              </a>
            )}
          </div>
        </header>

        <div className="prose mb-10 text-foreground">
          {article.body.split("\n").map((paragraph, i) => {
            if (!paragraph.trim()) return null
            return <p key={i}>{paragraph}</p>
          })}
        </div>

        {article.claims.length > 0 && (
          <section className="mb-10 rounded-xl border border-border bg-card p-6">
            <h2 className="text-lg font-semibold mb-4">Verifikasi Faktual</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Berikut adalah klaim-klaim yang teridentifikasi dalam artikel ini beserta hasil verifikasinya:
            </p>
            <div className="space-y-4">
              {article.claims.map((claim, i) => (
                <div key={i} className="flex items-start gap-3">
                  <FactClaimTooltip claim={claim} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm leading-relaxed">{claim.claim}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="rounded-xl border border-border bg-muted/50 p-6">
          <h2 className="text-sm font-semibold mb-2">Tentang Artikel Ini</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Artikel ini diproduksi secara otomatis oleh NewsAgent, sistem multi-agen AI yang terdiri dari
            12 agen khusus yang bekerja secara berurutan: dari penulisan draf, pengecekan fakta, verifikasi
            klaim, skoring kredibilitas, hingga publikasi. Setiap klaim dalam artikel telah diverifikasi
            terhadap sumber eksternal dan diberi skor kepercayaan. Skor kredibilitas keseluruhan dihitung
            berdasarkan akurasi faktual, konsistensi narasi, resolusi konflik, dan kualitas sumber.
          </p>
        </section>

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "NewsArticle",
              headline: article.title,
              datePublished: article.created_at,
              dateModified: article.updated_at || article.created_at,
              wordCount: wordCount,
              author: {
                "@type": "Organization",
                name: "NewsAgent AI",
              },
              publisher: {
                "@type": "Organization",
                name: "NewsAgent",
              },
              mainEntityOfPage: {
                "@type": "WebPage",
                "@id": `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3001"}/berita/${article.article_id}`,
              },
            }),
          }}
        />
      </div>
    </article>
  )
}
