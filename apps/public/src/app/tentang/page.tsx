import { Shield, Network, Brain, Eye, Scale, BookOpen } from "lucide-react"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Tentang Sistem",
  description:
    "Pelajari cara kerja NewsAgent — sistem produksi berita berbasis AI multi-agen dengan verifikasi faktual transparan.",
}

const values = [
  {
    icon: Shield,
    title: "Akurasi di Atas Kecepatan",
    desc: "Setiap artikel melewati 12 agen AI yang memverifikasi fakta, memeriksa konsistensi, dan memberi skor kredibilitas sebelum publikasi.",
  },
  {
    icon: Eye,
    title: "Transparansi Algoritmik",
    desc: "Skor kredibilitas, sumber verifikasi, dan log debat antar agen ditampilkan secara terbuka untuk setiap artikel yang dipublikasikan.",
  },
  {
    icon: Brain,
    title: "Verifikasi Faktual Multi-Lapis",
    desc: "Fact-check pipeline terdiri dari 4 sub-agen: ekstraksi klaim, pembuatan query pencarian, pengumpulan bukti, dan prediksi putusan.",
  },
  {
    icon: Scale,
    title: "Debat Delphi untuk Konsensus",
    desc: "Aggregator menjalankan 2 ronde debat untuk menyelesaikan konflik antar sumber sebelum artikel final diproduksi.",
  },
  {
    icon: Network,
    title: "Arsitektur Hierarkis",
    desc: "Orchestrator Agent mengkoordinasikan seluruh pipeline: RAG → Draft → Editor → Fact-Check → Aggregator → Quality Gate → Publisher.",
  },
  {
    icon: BookOpen,
    title: "Skor Kredibilitas Terbuka",
    desc: "Quality Gate menilai artikel berdasarkan 4 komponen: akurasi faktual (40%), konsistensi narasi (25%), resolusi konflik (20%), dan kualitas sumber (15%).",
  },
]

const agents = [
  { name: "Orchestrator", role: "Koordinator pipeline, mengatur alur dan state" },
  { name: "RAG Pipeline", role: "Mengumpulkan konteks dari sumber web" },
  { name: "Draft Agent", role: "Menulis draf awal artikel" },
  { name: "Editor Agent", role: "Memperbaiki tata bahasa dan struktur" },
  { name: "Input Ingestion", role: "Mengidentifikasi klaim dalam artikel" },
  { name: "Query Generation", role: "Membuat query pencarian untuk tiap klaim" },
  { name: "Evidence Retrieval", role: "Mengumpulkan bukti dari web" },
  { name: "Verdict Prediction", role: "Menentukan status tiap klaim" },
  { name: "Aggregator", role: "Debat 2 ronde untuk konsensus" },
  { name: "Quality Gate", role: "Memberi skor kredibilitas 0.0-1.0" },
  { name: "Memory Agent", role: "Mencatat metrik dan knowledge graph" },
  { name: "Publisher", role: "Menerbitkan artikel ke CMS" },
]

export default function AboutPage() {
  return (
    <div>
      <section className="border-b border-border bg-gradient-to-b from-primary/5 to-background">
        <div className="container py-12 md:py-16 text-center">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
            Tentang NewsAgent
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Sistem produksi berita otonom berbasis AI multi-agen yang transparan dan dapat diverifikasi.
          </p>
        </div>
      </section>

      <section className="container py-12">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Visi</h2>
          <p className="text-muted-foreground leading-relaxed mb-8">
            Menjadi infrastruktur produksi berita yang otonom, akurat, dan transparan,
            di mana setiap artikel yang diterbitkan dapat diverifikasi secara ilmiah dan sistematis.
            NewsAgent dibangun di atas prinsip akurasi di atas kecepatan, transparansi algoritmik,
            dan kedaulatan manusia dalam pengambilan keputusan editorial.
          </p>

          <h2 className="text-2xl font-bold mb-6">Nilai-nilai Inti</h2>
          <div className="grid gap-5 md:grid-cols-2 mb-12">
            {values.map((v) => {
              const Icon = v.icon
              return (
                <div key={v.title} className="flex gap-4 rounded-xl border border-border bg-card p-5">
                  <Icon className="size-6 text-primary shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1 text-sm">{v.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{v.desc}</p>
                  </div>
                </div>
              )
            })}
          </div>

          <h2 className="text-2xl font-bold mb-4">Cara Kerja</h2>
          <div className="text-muted-foreground leading-relaxed mb-8 space-y-3">
            <p>
              NewsAgent menggunakan arsitektur Hierarchical Multi-Agent System (HMAS) yang terdiri dari
              12 agen AI spesialis yang bekerja secara berurutan. Tidak seperti flat MAS di mana semua agen
              setara, HMAS memiliki struktur komando hierarkis dengan Orchestrator Agent di puncak.
            </p>
            <p>
              Pipeline dimulai ketika sebuah topik, draf mentah, atau URL sumber dimasukkan.
              RAG Pipeline mengumpulkan konteks dari web, Draft Agent menulis artikel,
              Fact-Check Pipeline memverifikasi setiap klaim, Aggregator menjalankan debat
              untuk mencapai konsensus, Quality Gate memberi skor kredibilitas, dan akhirnya
              Publisher menerbitkan artikel ke CMS.
            </p>
          </div>

          <h2 className="text-2xl font-bold mb-6">12 Agen Pipeline</h2>
          <div className="grid gap-3 md:grid-cols-2 mb-12">
            {agents.map((a) => (
              <div key={a.name} className="flex items-center gap-3 rounded-lg border border-border bg-card p-3">
                <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-mono text-xs font-bold shrink-0">
                  {a.name.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <div className="font-medium text-sm">{a.name}</div>
                  <div className="text-xs text-muted-foreground">{a.role}</div>
                </div>
              </div>
            ))}
          </div>

          <section className="rounded-xl border border-border bg-muted/50 p-6 mb-8">
            <h2 className="text-lg font-semibold mb-3">Label Verifikasi</h2>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              Setiap artikel yang dipublikasikan melalui NewsAgent dilengkapi dengan label verifikasi
              yang menunjukkan tingkat kepercayaan sistem terhadap keakuratan konten:
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="size-3 rounded-full bg-accent shrink-0" />
                <div>
                  <div className="text-sm font-medium">Terverifikasi (≥75%)</div>
                  <div className="text-xs text-muted-foreground">
                    Artikel telah melewati seluruh pipeline verifikasi dengan skor tinggi.
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="size-3 rounded-full bg-yellow-400 shrink-0" />
                <div>
                  <div className="text-sm font-medium">Perlu Review (50-74%)</div>
                  <div className="text-xs text-muted-foreground">
                    Beberapa klaim memerlukan verifikasi manual oleh editor.
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="size-3 rounded-full bg-destructive shrink-0" />
                <div>
                  <div className="text-sm font-medium">Kredibilitas Rendah (&lt;50%)</div>
                  <div className="text-xs text-muted-foreground">
                    Artikel memerlukan revisi penuh sebelum dapat dipertimbangkan untuk publikasi.
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </div>
  )
}
