import { notFound } from "next/navigation"
import { api } from "@/lib/api"
import { ArticleCard } from "@/components/home/article-card"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import type { Metadata } from "next"

type Props = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const { categories } = await api.categories.list()
  const cat = categories.find((c) => c.slug === slug)
  return {
    title: cat ? `${cat.name} — Kategori` : "Kategori",
    description: `Artikel kategori ${cat?.name || slug} di NewsAgent`,
  }
}

export const dynamic = "force-dynamic"
export const revalidate = 0

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params
  const [{ articles, total }, { categories }] = await Promise.all([
    api.articles.list({ category: slug, limit: 50, sort: "latest" }),
    api.categories.list(),
  ])

  const cat = categories.find((c) => c.slug === slug)
  if (!cat && articles.length === 0) notFound()

  const name = cat?.name || slug

  return (
    <div className="container py-8 md:py-12">
      <Link href="/" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground no-underline hover:text-foreground mb-6 transition-colors">
        <ArrowLeft className="size-4" />
        Kembali ke Beranda
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">{name}</h1>
        <p className="text-muted-foreground">{total} artikel dalam kategori ini</p>
      </div>

      {articles.length === 0 ? (
        <p className="text-muted-foreground py-16 text-center">
          Belum ada artikel dalam kategori ini.
        </p>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((a) => (
            <ArticleCard key={a.article_id} article={a} />
          ))}
        </div>
      )}
    </div>
  )
}
