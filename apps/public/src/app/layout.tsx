import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" })
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" })

export const metadata: Metadata = {
  title: {
    default: "NewsAgent — Berita Terverifikasi AI",
    template: "%s | NewsAgent",
  },
  description:
    "Platform berita berbasis AI multi-agen. Setiap artikel diverifikasi secara faktual dengan skor kredibilitas transparan.",
  openGraph: {
    type: "website",
    locale: "id_ID",
    siteName: "NewsAgent",
  },
  other: {
    "og:site_name": "NewsAgent",
    "article:author": "NewsAgent AI",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className={`${geist.variable} ${geistMono.variable} font-sans antialiased min-h-dvh flex flex-col`}>
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
