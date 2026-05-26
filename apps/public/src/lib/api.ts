export type PublicArticle = {
  id: string
  article_id: string
  title: string
  body: string
  excerpt: string
  credibility_score: number
  category: string
  input_type: string
  source_url: string | null
  published_url: string | null
  claims: Claim[]
  revision_count: number
  created_at: string | null
  updated_at: string | null
  events?: EventDict[]
}

export type Claim = {
  claim: string
  verdict: "verified" | "false" | "unverified"
  evidence: string
  trust_score?: number
}

export type EventDict = {
  type: string
  agent: string
  action: string
  detail: string
  created_at: string
}

export type ArticleListResponse = {
  total: number
  page: number
  limit: number
  articles: PublicArticle[]
}

export type Category = {
  slug: string
  name: string
  count: number
}

export type PublicStats = {
  total_articles: number
  avg_credibility_score: number
  latest_article_at: string | null
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
    next: { revalidate: 60 },
  })
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  articles: {
    list(params?: {
      page?: number
      limit?: number
      category?: string
      sort?: "latest" | "score"
      min_score?: number
    }) {
      const q = new URLSearchParams()
      if (params?.page) q.set("page", String(params.page))
      if (params?.limit) q.set("limit", String(params.limit))
      if (params?.category) q.set("category", params.category)
      if (params?.sort) q.set("sort", params.sort)
      if (params?.min_score) q.set("min_score", String(params.min_score))
      const qs = q.toString()
      return request<ArticleListResponse>(`/api/v1/public/articles${qs ? `?${qs}` : ""}`)
    },
    get(id: string) {
      return request<PublicArticle>(`/api/v1/public/articles/${encodeURIComponent(id)}`)
    },
  },
  categories: {
    list() {
      return request<{ categories: Category[] }>("/api/v1/public/categories")
    },
  },
  stats: {
    get() {
      return request<PublicStats>("/api/v1/public/stats")
    },
  },
}
