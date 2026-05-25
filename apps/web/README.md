# 🖥️ NewsAgent Frontend — Dashboard Redaksi & Situs Berita

Aplikasi Next.js untuk sistem NewsAgent. Terdiri dari dua layer:

| Layer | Pengguna | Tujuan |
|---|---|---|
| **Dashboard Redaksi** | Editor, jurnalis, admin | Mengelola pipeline, memantau agen, review artikel |
| **Situs Berita Publik** | Pembaca | Membaca artikel, melihat label verifikasi fakta |

## Tech Stack

- **Framework:** Next.js 14 (App Router) — TypeScript
- **UI:** shadcn/ui + Tailwind CSS v4
- **State Management:** Zustand
- **Real-time:** WebSocket (status pipeline live)
- **Charts:** Recharts

## Prasyarat

- Node.js 18+
- pnpm 10.x
- Backend NewsAgent berjalan di `localhost:8000`

## Memulai

```bash
pnpm install
pnpm dev
```

Buka [http://localhost:3000](http://localhost:3000).

## Struktur Halaman

### Dashboard Redaksi
| Route | Halaman |
|---|---|
| `/dashboard` | Ringkasan aktivitas sistem |
| `/pipeline` | Visualisasi status agen real-time |
| `/articles` | Manajemen artikel |
| `/articles/[id]` | Detail + review artikel |
| `/articles/new` | Input artikel baru |
| `/settings` | Konfigurasi parameter sistem |

### Situs Berita Publik
| Route | Halaman |
|---|---|
| `/` | Beranda — artikel terbaru |
| `/berita/[slug]` | Detail artikel + label verifikasi |
| `/kategori/[slug]` | Artikel per kategori |
| `/tentang` | Cara kerja sistem |

## Spesifikasi Lengkap

Lihat [FRONTEND.md](../../FRONTEND.md) untuk spesifikasi detail, komponen UI, dan alur pengguna.
