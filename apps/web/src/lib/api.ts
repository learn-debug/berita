import { redirectToLogin } from "./auth-redirect";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export interface VerdictRaw {
  claim: string;
  premis_fakta: string;
  premis_bukti: string;
  premis_sumber: string;
  analisis: string;
  putusan: "SUPPORTED" | "REFUTED" | "NOT_ENOUGH_EVIDENCE";
  alasan: string;
  keyakinan: "TINGGI" | "SEDANG" | "RENDAH";
}

export interface FactCheckReport {
  claims?: string;
  queries?: string;
  evidence?: string;
  verdict?: string;
  verdict_raw?: VerdictRaw[];
}

export interface EventDict {
  agent: string;
  action: string;
  detail: string | null;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface ArticleState {
  article_id: string;
  input_type: string;
  raw_input: string;
  rag_context: string;
  draft: string;
  edited_draft: string;
  aggregated_article: string;
  fact_check_report: FactCheckReport;
  credibility_score: number | null;
  status: string;
  revision_count: number;
  events: EventDict[];
  published_title?: string;
  published_body?: string;
  published_url?: string | null;
  created_at: number;
  updated_at: number;
}

export interface ArticleListResponse {
  total: number;
  page: number;
  limit: number;
  articles: ArticleState[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api/v1${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    if (res.status === 401) {
      redirectToLogin();
    }
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  return res.json();
}

export const api = {
  processArticle: (input_type: string, raw_input: string) =>
    request<{ article_id: string; status: string; message: string }>("/articles/process", {
      method: "POST",
      body: JSON.stringify({ input_type, raw_input }),
    }),

  listArticles: (params?: {
    status?: string;
    min_score?: number;
    page?: number;
    limit?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.min_score !== undefined) qs.set("min_score", String(params.min_score));
    if (params?.page) qs.set("page", String(params.page));
    if (params?.limit) qs.set("limit", String(params.limit));
    const q = qs.toString();
    return request<ArticleListResponse>(`/articles${q ? `?${q}` : ""}`);
  },

  getArticle: (id: string) => request<ArticleState>(`/articles/${id}`),

  patchArticle: (id: string, action: string, content?: string) =>
    request<ArticleState>(`/articles/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ action, content }),
    }),
};
