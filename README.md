# 🤖 NewsAgent — Multi-Agent System untuk Otomatisasi Situs Berita

> Sistem multi-agent berbasis AI yang memproses draf artikel secara mandiri, melakukan pengecekan fakta otomatis, dan mempublikasikan konten secara kolaboratif.

---

## 📌 Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Daftar Agen](#daftar-agen)
- [Alur Kerja](#alur-kerja)
- [Tech Stack](#tech-stack)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Konfigurasi](#konfigurasi)
- [Dokumen Terkait](#dokumen-terkait)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

---

## Gambaran Umum

**NewsAgent** adalah sistem multi-agent yang dirancang untuk mengotomatisasi alur produksi konten berita. Sistem ini terdiri dari beberapa agen AI yang bekerja secara **paralel dan kolaboratif** — mulai dari penulisan draf, pengecekan fakta berbasis bukti, pengeditan, hingga publikasi otomatis ke CMS.

### Masalah yang Diselesaikan

| Masalah Konvensional | Solusi NewsAgent |
|---|---|
| Proses redaksi lambat & manual | Pipeline otomatis end-to-end (HMAS) |
| Fakta tidak terverifikasi sebelum tayang | Fact-Check pipeline 4 sub-agen paralel |
| Verifikasi tidak transparan | Debate + consensus multi-agen |
| Skor kelayakan artikel biner | Credibility scoring (0–1) yang granular |
| Halusinasi LLM pada RAG | Structured evidence summarization |
| Terkunci satu LLM provider | LLM Adapter Layer dengan auto-fallback |
| Pipeline berhenti jika satu agen gagal | Circuit Breaker + Dead Letter Queue |
| State antar agen tidak konsisten | Immutable state schema + LangGraph |
| Biaya API tidak terprediksi | Token budget per agen + cost tracker |
| Rentan prompt injection | Input sanitization + prompt hardening |
| Tidak ada rekam jejak draf | Memory Layer terpusat (pgvector + PostgreSQL) |

---

## Arsitektur Sistem

Arsitektur NewsAgent terdiri dari pipeline multi-agent (LangGraph) dengan spesialisasi per peran:
- Fact-Check Agent dipecah menjadi **4 sub-agen** spesialis
- Review & Aggregator menggunakan **debate + consensus**
- Quality Gate menggunakan **credibility score 0–1**
- Memory Agent sebagai pengelola knowledge graph dan rekam draf
- RAG pipeline menggunakan **structured evidence summarization**

```mermaid
flowchart TB
    subgraph Input["INPUT"]
        I[Topik / Draf Mentah / URL]
    end

    I --> RAG[RAG Pipeline<br/>Structured Evidence]

    RAG --> O[Orchestrator Agent<br/>Koordinasi & Pembagian Tugas]

    O --> D[Draft Agent<br/>Tulis & Susun Artikel]

    D --> |route_after_draft| CheckDraft{Status Revisi?}
    CheckDraft --> |Ya| O
    CheckDraft --> |Tidak| E[Editor Agent<br/>Tata Bahasa & Gaya]

    E --> FC1[Fact-Check: Input Ingestion]

    subgraph FCP["Fact-Check Pipeline"]
        FC1 --> FC2[Query Generation]
        FC2 --> FC3[Evidence Retrieval]
        FC3 --> FC4[Verdict Prediction]
    end

    FC4 --> AG[Aggregator<br/>Debate + Consensus]

    AG --> QG[Quality Gate<br/>Credibility Score 0-1]

    QG -->|>= 0.75| Mem[Memory Agent<br/>Cache & Graph]
    QG -->|0.50 - 0.74| Review[⚠️ Review Editor<br/>Human-in-the-loop]
    QG -->|< 0.50| Revise[🔄 Revisi Penuh]

    Review --> |Sudah 2x revisi| Mem
    Review --> |Belum 2x revisi| E

    Revise --> |Sudah 2x revisi| Mem
    Revise --> |Belum 2x revisi| O

    Mem --> Pub[Publisher Agent<br/>Publikasi ke CMS]
```

> **Catatan:** Pipeline berjalan sekuensial (12 node LangGraph) dengan routing conditional untuk review/revisi (maks 2x revisi). Lihat [Diagram Pipeline](docs/ARCHITECTURE.md#diagram-pipeline-langgraph) untuk detail implementasi.

---

## Daftar Agen

### 1. Orchestrator Agent
Bertindak sebagai koordinator utama. Menerima input berupa topik atau draf mentah, lalu menganalisis dan mendelegasikan tugas ke agen-agen spesialis secara paralel.

### 2. RAG Pipeline *(Structured Evidence Summarization)*
Setiap dokumen yang diambil diproses terlebih dahulu menjadi ringkasan terstruktur sebelum diteruskan, sehingga mengurangi risiko halusinasi LLM.

### 3. Draft Agent
Bertugas menyusun dan memperbaiki struktur narasi artikel berdasarkan topik atau draf awal yang diberikan, dengan menginjeksi contoh draf skor tinggi dari *Memory Layer*.

### 4. Fact-Check Pipeline *(4 Sub-Agen)*
Proses fact-checking dipecah menjadi 4 sub-agen spesialis yang bekerja secara sekuensial:
- **4a. Input Ingestion Agent**: Dekomposisi artikel menjadi klaim-klaim.
- **4b. Query Generation Agent**: Membuat subquery pencarian terarah.
- **4c. Evidence Retrieval Agent**: Mengambil bukti dari sumber terpercaya (parallel web search).
- **4d. Verdict Prediction Agent**: Mensintesis bukti menjadi putusan (benar/salah/tak dapat diverifikasi).

### 5. Editor Agent
Memperbaiki kualitas bahasa, konsistensi gaya, dan struktur kalimat sesuai pedoman redaksi.

### 6. Review & Aggregator *(Debate + Consensus)*
Aggregator menggunakan metode debat di mana beberapa agen dengan perspektif berbeda memberikan penilaian independen, mendeteksi konflik, lalu mencapai konsensus.

### 7. Quality Gate *(Credibility Scoring)*
Menggantikan pendekatan lolos/gagal biner dengan sistem skor kredibilitas 0–1.
- `score ≥ 0.75` → lanjut ke Memory Agent
- `0.50 ≤ score < 0.75` → revisi parsial (kembali ke Editor Agent)
- `score < 0.50` → revisi penuh (kembali ke Orchestrator)
*(Maksimal 2x revisi, setelah itu artikel dipaksa lanjut ke Memory Agent).*

### 8. Memory Agent
Menyimpan metrik artikel, *verdict cache*, draf akhir, serta mengekstrak entitas ke dalam Knowledge Graph (PostgreSQL + pgvector).

### 9. Publisher Agent
Menerima artikel final dari Memory Agent dan mempublikasikannya ke CMS (misalnya WordPress) sesuai jadwal.

---

## Alur Kerja

```
1. Input diterima (topik / draf mentah / URL sumber)
2. RAG Pipeline mengambil & mensintesis bukti terstruktur
3. Orchestrator mendistribusikan tugas awal
4. Draft Agent membuat draf (bisa looping ke Orchestrator jika status revisi)
5. Editor Agent memperbaiki bahasa
6. Fact-Check Pipeline (4 sub-agen) berjalan sekuensial menguji fakta
7. Review & Aggregator:
   a. Deteksi konflik antar output agen
   b. Debat & sintesis konsensus
8. Quality Gate menghitung credibility score (0–1):
   - score ≥ 0.75  → Memory Agent
   - 0.50–0.74     → revisi ke Editor Agent (max 2x)
   - < 0.50        → revisi ke Orchestrator (max 2x)
9. Memory Agent merekam riwayat, entitas, dan cache
10. Publisher Agent mempublikasikan ke CMS
```

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| **Framework Multi-Agent** | LangGraph |
| **LLM Adapter Layer** | Claude, OpenAI, Gemini, Mistral, Qwen, DeepSeek, HuggingFace, OpenRouter |
| **Failover Mechanism** | `FallbackAdapter` (Auto-fallback LLM provider saat kuota habis) |
| **Frontend Dashboard** | Next.js 16.2.6, React 19, Tailwind CSS v4, shadcn/ui |
| **Autentikasi** | JWT Auth (`pyjwt`, `cryptography`) |
| **Memory & Database** | PostgreSQL 17 + pgvector (Knowledge Graph & Cache) |
| **Cache & Queue** | Redis 7 (Docker) |
| **Search Provider** | Tavily (default), Serper |
| **Backend API** | Python 3.10+ / FastAPI / Pydantic |
| **Resilience** | Tenacity (retry), Circuit Breaker, DLQ |
| **Cost Control** | Token budget per agen + tracker |
| **Tooling Tambahan** | NER Extractor (spaCy) |

---

## Struktur Proyek

Proyek ini dibangun menggunakan struktur **pnpm monorepo**.

```
borneo/
├── apps/
│   └── web/                                 # Frontend Dashboard Redaksi (Next.js 16)
│       ├── src/
│       │   ├── app/                         # App Router (dashboard, articles, pipeline, dll)
│       │   ├── components/                  # UI Components (shadcn, charts)
│       │   ├── hooks/                       # Custom hooks (e.g., use-websocket)
│       │   └── lib/                         # Utilities (API client, auth)
│       └── package.json                     # Frontend dependencies
├── backend/
│   ├── newsagent/                           # Core Backend Python HMAS
│   │   ├── agents/                          # 12 Agen LangGraph (Orchestrator, Draft, dll)
│   │   ├── api/                             # FastAPI App (routers, websockets, auth)
│   │   ├── core/                            # LangGraph workflow (graph.py), config
│   │   ├── cost/                            # Token budget & cost tracking
│   │   ├── database/                        # Repository layer & schema.sql
│   │   ├── llm/                             # LLM Adapters (Claude, OpenAI, Fallback, dll)
│   │   ├── memory/                          # DraftMemory, VerdictCache, Engine (pgvector)
│   │   ├── prompts/                         # Markdown prompt templates
│   │   ├── rag/                             # Retriever, Synthesizer, Reranker
│   │   ├── resilience/                      # Retry policy, Circuit Breaker, DLQ
│   │   ├── security/                        # Input Sanitizer, Prompt Hardening, Rate Limiter
│   │   ├── tools/                           # Web Search, NER Extractor, CMS Client
│   │   ├── utils/                           # Helper functions
│   │   └── tests/                           # Unit & Integration Tests (263 passing)
│   ├── pyproject.toml                       # Python deps (uv, ruff, pytest)
│   └── uv.lock
├── packages/                                # Shared packages (akan datang)
├── docs/                                    # Dokumentasi arsitektur, ADR, deployment
├── docker-compose.yml                       # PostgreSQL & Redis infrastructure
├── pnpm-workspace.yaml                      # Root pnpm monorepo config
└── package.json
```

---

## Instalasi

Lihat panduan lengkap di [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — mencakup prasyarat, setup lokal, konfigurasi Docker, dan variabel environment.

Instalasi cepat:

```bash
# 1. Install dependensi backend (Python) dengan uv
uv sync --extra dev --directory backend

# 2. Install dependensi frontend (Node.js) dengan pnpm
pnpm install

# 3. Konfigurasi
cp .env.example .env

# 4. Jalankan infrastruktur (PostgreSQL + Redis)
docker compose up -d

# 5. Jalankan Backend API
uvicorn newsagent.api.main:app --reload --app-dir backend

# 6. Jalankan Frontend Dashboard (di terminal baru)
pnpm run dev --filter web
```

---

## Konfigurasi

Buat file `.env` di root proyek (isi sesuai `.env.example`):

```env
# === LLM API Keys ===
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=sk-...

# === Fallback Chain ===
LLM_FALLBACK_CHAIN=gemini,openrouter,hf

# === Search Provider ===
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly-...

# === Database & Cache ===
DATABASE_URL=postgresql+asyncpg://newsagent:newsagent_dev@localhost:5432/newsagent
REDIS_URL=redis://localhost:6379/0
```

---

## Roadmap

Lihat [ROADMAP.md](./ROADMAP.md) untuk detail lengkap. Saat ini **Fase 1 (Fondasi)** dan **Fase 2 (Dashboard Redaksi)** telah selesai.

---

## Kontribusi

Silakan baca [CONTRIBUTING.md](./CONTRIBUTING.md) sebelum membuka _Pull Request_. Semua agen wajib mematuhi aturan dalam [GEMINI.md](./GEMINI.md).

---

## Lisensi

Didistribusikan di bawah lisensi **Apache 2.0**. Lihat file `LICENSE` untuk detail lebih lanjut.
