# 🖥️ NewsAgent — Spesifikasi Frontend

## Daftar Isi

- [Gambaran Dua Layer](#gambaran-dua-layer)
- [Layer 1 — Dashboard Redaksi](#layer-1--dashboard-redaksi-internal)
- [Layer 2 — Situs Berita Publik](#layer-2--situs-berita-publik)
- [Hubungan Frontend ↔ Backend](#hubungan-frontend--backend)
- [Urutan Pengembangan yang Disarankan](#urutan-pengembangan-yang-disarankan)


Sistem frontend NewsAgent terdiri dari dua layer terpisah dengan tujuan dan pengguna yang berbeda.

---

## Gambaran Dua Layer

| Layer | Pengguna | Tujuan |
|---|---|---|
| **Dashboard Redaksi** | Editor, jurnalis, admin | Mengelola pipeline, memantau agen, review artikel |
| **Situs Berita Publik** | Pembaca | Membaca artikel, melihat label verifikasi fakta |

---

## Layer 1 — Dashboard Redaksi (Internal)

### Teknologi yang Direkomendasikan
- **Framework:** Next.js 16 (App Router) — **TypeScript**
- **UI Component:** shadcn/ui + Tailwind CSS v4
- **State Management:** Zustand
- **Real-time:** WebSocket (status pipeline live)
- **Charts:** Recharts
- **Auth:** NextAuth.js

---

### Halaman & Fitur

#### 1. Dashboard Utama (`/dashboard`)
Halaman pertama yang dilihat setelah login. Menampilkan ringkasan aktivitas sistem.

**Konten:**
- Metric cards: artikel diproses hari ini, rata-rata credibility score, artikel antri, artikel gagal
- Grafik aktivitas pipeline (7 hari terakhir)
- Daftar artikel terbaru beserta status pipeline real-time
- Notifikasi: artikel yang butuh review manual (skor < 0.75)

---

#### 2. Halaman Pipeline (`/pipeline`)
Pusat kendali utama untuk memantau alur kerja semua agen secara real-time.

**Konten:**
- Visualisasi status tiap agen (Orchestrator, RAG, Draft, Fact-Check, Editor, Aggregator, Publisher)
- Status setiap agen: `idle` / `running` / `waiting` / `error`
- Log aktivitas live per agen (stream)
- Tombol: pause pipeline, retry agen yang gagal, skip ke tahap berikutnya

**Status warna:**
- Hijau → agen aktif berjalan
- Abu-abu → idle / menunggu
- Kuning → menunggu input dari agen lain
- Merah → error, butuh intervensi

---

#### 3. Halaman Artikel (`/articles`)
Manajemen semua artikel dalam sistem.

**Konten:**
- Tabel artikel dengan kolom: judul, status, credibility score, tanggal, aksi
- Filter: status (draft / processing / review / published / failed), skor, tanggal
- Pencarian judul artikel
- Bulk action: publish, reject, retry

**Status artikel:**
- `processing` → sedang diproses agen
- `review` → menunggu persetujuan editor (skor 0.50–0.74)
- `approved` → lolos quality gate, siap publish
- `published` → sudah tayang
- `failed` → gagal, butuh input manual

---

#### 4. Halaman Detail Artikel (`/articles/[id]`)
Halaman paling penting untuk editor — tempat review dan approval artikel.

**Konten:**

*Panel kiri — Artikel:*
- Preview artikel final (hasil kerja agen)
- Editor teks inline (bisa diedit sebelum publish)
- Tombol: Approve & Publish, Kirim Ulang ke Agen, Tolak

*Panel kanan — Laporan Agen:*
- **Credibility Score:** gauge 0–1 dengan breakdown per komponen
- **Fact-Check Report:** daftar semua klaim yang diverifikasi
  - Tiap klaim: teks klaim, status (verified / false / unverified), sumber bukti, skor kepercayaan
  - Klaim bermasalah di-highlight merah di teks artikel
- **Editor Agent Report:** perubahan tata bahasa yang dilakukan
- **Debate Log:** ringkasan ronde debat antar agen (DelphiAgent pattern)
- **Sumber RAG:** daftar dokumen yang digunakan sebagai konteks

---

#### 5. Halaman Input Artikel (`/articles/new`)
Form untuk memasukkan artikel baru ke pipeline.

**Konten:**
- Pilihan tipe input: Topik, Draf Mentah, URL Sumber
- Field konten utama (textarea atau URL)
- Pengaturan: target jumlah kata, jadwal publikasi, kategori
- Tombol: Kirim ke Pipeline

---

#### 6. Halaman Pengaturan (`/settings`)
Konfigurasi parameter sistem.

**Konten:**
- **Quality Gate:** atur threshold credibility score
- **Fact-Check:** jumlah sumber maksimum per klaim, threshold kredibilitas sumber
- **Aggregator:** jumlah ronde debat maksimum, threshold konsensus
- **Publisher:** koneksi ke CMS, jadwal default publikasi
- **Notifikasi:** email / Slack untuk alert artikel gagal atau butuh review

---

### Komponen UI Utama

```
components/
├── pipeline/
│   ├── AgentStatusCard.tsx       # Status tiap agen (idle/running/error)
│   ├── PipelineVisualizer.tsx    # Visualisasi alur pipeline real-time
│   └── AgentLog.tsx              # Log stream aktivitas agen
├── articles/
│   ├── ArticleTable.tsx          # Tabel daftar artikel
│   ├── ArticleEditor.tsx         # Editor teks inline
│   ├── CredibilityGauge.tsx      # Gauge skor 0–1
│   ├── FactCheckReport.tsx       # Laporan verifikasi klaim
│   └── DebateLog.tsx             # Log ronde debat agen
├── dashboard/
│   ├── MetricCard.tsx            # Kartu angka ringkasan
│   └── ActivityChart.tsx         # Grafik aktivitas harian
└── shared/
    ├── StatusBadge.tsx           # Badge status artikel/agen
    └── ScoreBar.tsx              # Bar skor credibility
```

---

### Alur Pengguna Utama (Editor)

```
Login
  └── Dashboard (lihat ringkasan)
        └── Pipeline (pantau agen berjalan)
              └── Artikel masuk status "review"
                    └── Detail Artikel
                          ├── Baca laporan fact-check
                          ├── Edit teks jika perlu
                          └── Approve & Publish / Tolak
```

---

## Layer 2 — Situs Berita Publik

### Teknologi yang Direkomendasikan
- **Framework:** Next.js 16 (App Router + SSG/ISR)
- **Styling:** Tailwind CSS v4
- **CMS:** Headless CMS (Strapi / WordPress) sebagai sumber konten
- **SEO:** next/head + structured data (schema.org)

---

### Halaman & Fitur

#### 1. Halaman Beranda (`/`)
- Hero section: artikel utama
- Grid artikel terbaru per kategori
- Sidebar: artikel trending, tag populer

#### 2. Halaman Artikel (`/berita/[slug]`)
Tampilan artikel untuk pembaca. Fitur khas NewsAgent yang membedakan dari situs berita biasa:

**Label Verifikasi Fakta:**
- Badge "Terverifikasi AI" dengan credibility score yang ditampilkan secara transparan
- Klaim-klaim kunci dalam artikel diberi tanda khusus
- Klik pada klaim → tooltip menampilkan sumber verifikasi dan skor kepercayaan
- Label warna: hijau (verified), abu-abu (tidak dapat diverifikasi)

**Konten lain:**
- Teks artikel penuh
- Informasi penulis / "Ditulis oleh NewsAgent AI"
- Waktu pemrosesan pipeline (opsional, untuk transparansi)
- Artikel terkait

#### 3. Halaman Kategori (`/kategori/[slug]`)
- Grid artikel per kategori
- Filter: terbaru, terpopuler, credibility score tertinggi

#### 4. Halaman Tentang (`/tentang`)
- Penjelasan cara kerja sistem multi-agent untuk pembaca awam
- Metodologi fact-checking yang digunakan
- Transparansi: referensi riset akademis yang mendasari sistem

---

### Komponen UI Utama

```
components/
├── article/
│   ├── ArticleHeader.tsx         # Judul, meta, badge verifikasi
│   ├── ArticleBody.tsx           # Konten dengan klaim ter-highlight
│   ├── FactClaimTooltip.tsx      # Tooltip sumber verifikasi
│   └── CredibilityBadge.tsx      # Badge skor + label
├── layout/
│   ├── Navbar.tsx
│   ├── Footer.tsx
│   └── Sidebar.tsx
└── home/
    ├── HeroArticle.tsx
    └── ArticleGrid.tsx
```

---

## Hubungan Frontend ↔ Backend

```
Dashboard Redaksi
  │
  ├── REST API  → /api/articles, /api/pipeline, /api/agents
  └── WebSocket → ws://server/pipeline/[id]  (status real-time)

Situs Berita Publik
  │
  └── CMS API (Headless) → artikel yang sudah publish + metadata fact-check
```

---

## Urutan Pengembangan yang Disarankan

Lihat [ROADMAP.md](./ROADMAP.md) untuk urutan dan estimasi waktu lengkap. Secara garis besar untuk frontend:

- Dashboard Redaksi dibangun lebih dulu (Fase 2 ROADMAP)
- Situs Berita Publik menyusul setelah pipeline stabil (Fase 3 ROADMAP)

---

*Dokumen ini adalah spesifikasi frontend untuk proyek NewsAgent. Lihat README.md untuk arsitektur backend dan ROADMAP.md untuk peta jalan pengembangan.*
