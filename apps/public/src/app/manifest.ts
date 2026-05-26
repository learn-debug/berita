import type { MetadataRoute } from "next"

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "NewsAgent — Berita Terverifikasi AI",
    short_name: "NewsAgent",
    description: "Platform berita berbasis AI multi-agen dengan verifikasi faktual transparan",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#6366f1",
  }
}
