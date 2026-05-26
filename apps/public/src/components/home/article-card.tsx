import Link from "next/link"
import { Calendar, BookOpen } from "lucide-react"
import { CredibilityBadge } from "@/components/article/credibility-badge"
import { cn, formatDate, truncate } from "@/lib/utils"
import type { PublicArticle } from "@/lib/api"

type Props = {
  article: PublicArticle
  featured?: boolean
}

export function ArticleCard({ article, featured }: Props) {
  return (
    <Link
      href={`/berita/${article.article_id}`}
      className={cn(
        "group block rounded-xl border border-border bg-card p-5 no-underline transition-all",
        "hover:shadow-lg hover:border-primary/30 hover:-translate-y-0.5",
        featured && "md:col-span-2 md:grid md:grid-cols-2 md:gap-6 md:p-6",
      )}
    >
      <div className={cn("space-y-3", featured && "flex flex-col justify-center")}>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
            {article.category}
          </span>
          {article.created_at && (
            <span className="inline-flex items-center gap-1">
              <Calendar className="size-3" />
              {formatDate(article.created_at)}
            </span>
          )}
        </div>
        <h3 className={cn("font-semibold leading-tight text-card-foreground group-hover:text-primary transition-colors", featured ? "text-2xl" : "text-base")}>
          {article.title}
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3">
          {truncate(article.excerpt, featured ? 300 : 150)}
        </p>
        <div className="flex items-center justify-between pt-1">
          <CredibilityBadge score={article.credibility_score} size="sm" />
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            <BookOpen className="size-3" />
            {article.body.split(" ").length} kata
          </span>
        </div>
      </div>
    </Link>
  )
}
