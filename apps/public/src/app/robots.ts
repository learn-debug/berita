import type { MetadataRoute } from "next"

const BASE = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3001"

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "GPTBot",
        allow: "/",
        disallow: "/api/",
      },
      {
        userAgent: "Google-Extended",
        allow: "/",
        disallow: "/api/",
      },
      {
        userAgent: "Claude-Web",
        allow: "/",
        disallow: "/api/",
      },
      {
        userAgent: "PerplexityBot",
        allow: "/",
        disallow: "/api/",
      },
      {
        userAgent: "*",
        allow: "/",
        disallow: "/api/",
      },
    ],
    sitemap: `${BASE}/sitemap.xml`,
  }
}
