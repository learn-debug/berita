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
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

---

## Gambaran Umum

**NewsAgent** adalah sistem multi-agent yang dirancang untuk mengotomatisasi alur produksi konten berita. Sistem ini terdiri dari beberapa agen AI yang bekerja secara **paralel dan kolaboratif** — mulai dari penulisan draf, pengecekan fakta berbasis bukti, pengeditan, hingga publikasi otomatis ke CMS.

### Masalah yang Diselesaikan

| Masalah Konvensional | Solusi NewsAgent | Dasar Riset |
|---|---|---|
| Proses redaksi lambat & manual | Pipeline otomatis end-to-end | AI-Press (2024) |
| Fakta tidak terverifikasi sebelum tayang | Fact-Check pipeline 4 sub-agen | FactAgent (2025) |
| Verifikasi tidak transparan | Debate + consensus multi-agen | DelphiAgent (2025) |
| Skor kelayakan artikel biner | Credibility scoring 0–1 | MAFC (2026) |
| Halusinasi LLM pada RAG | Structured evidence summarization | Frontiers AI (2025) |
| Terkunci satu LLM provider | LLM Adapter Layer — ganti provider via config | Adapter Pattern |
| Pipeline berhenti jika satu agen gagal | Circuit Breaker + Dead Letter Queue | Resilience Pattern |
| State antar agen tidak konsisten | Immutable state schema + event sourcing | Event Sourcing |
| Biaya API tidak terprediksi | Token budget per agen + tiered LLM | Cost Control |
| Rentan prompt injection | Input sanitization + prompt hardening | Security Layer |
| Verifikasi hanya dari web search biasa | OSINT Layer *(fase berikutnya)* | OSINT Integration |

---

## Arsitektur Sistem

Arsitektur NewsAgent terdiri dari pipeline multi-agent dengan spesialisasi per peran:
- Fact-Check Agent dipecah menjadi **4 sub-agen** spesialis
- Review & Aggregator menggunakan **debate + consensus**
- Quality Gate menggunakan **credibility score 0–1**
- RAG pipeline menggunakan **structured evidence summarization**

```mermaid
flowchart TB
    subgraph Input["INPUT"]
        I[Topik / Draf Mentah / URL]
    end

    I --> RAG[RAG Pipeline<br/>Structured Evidence]

    RAG --> O[Orchestrator Agent<br/>Koordinasi & Pembagian Tugas]

    O --> D[Draft Agent<br/>Tulis & Susun Artikel]
    O --> FC[Fact-Check Pipeline]
    O --> E[Editor Agent<br/>Tata Bahasa & Gaya]

    subgraph FCP["Fact-Check Pipeline"]
        FC1[1. Input Ingestion]
        FC2[2. Query Generation]
        FC3[3. Evidence Retrieval]
        FC4[4. Verdict Prediction]
        FC1 --> FC2 --> FC3 --> FC4
    end

    FC --> FC4

    D & FC4 & E --> AG[Aggregator<br/>Debate + Consensus]

    AG --> QG[Quality Gate<br/>Credibility Score 0-1]

    QG -->|>= 0.75| Pub[Publisher Agent<br/>Publikasi ke CMS]
    QG -->|0.50 - 0.74| Review[⚠️ Review Editor<br/>Human-in-the-loop]
    QG -->|< 0.50| Revise[🔄 Revisi Penuh]

    Review --> Pub
    Revise --> D
```

> **Catatan:** Pipeline berjalan sekuensial (11 node LangGraph) dengan routing conditional untuk review/revisi. Lihat [Diagram Pipeline](docs/ARCHITECTURE.md#diagram-pipeline-langgraph) untuk detail implementasi.

---

## Daftar Agen

### 1. Orchestrator Agent
Bertindak sebagai koordinator utama. Menerima input berupa topik atau draf mentah, lalu menganalisis dan mendelegasikan tugas ke agen-agen spesialis secara paralel.

**Tanggung jawab:**
- Parsing input dan penentuan prioritas
- Distribusi tugas ke agen spesialis
- Monitoring status tiap agen
- Menangani retry ketika ada agen yang gagal

---

### 2. RAG Pipeline *(Structured Evidence Summarization)*
> Didasarkan pada: **Frontiers AI (2025)**

Berbeda dari RAG konvensional, pipeline ini tidak menyuntikkan dokumen mentah ke prompt agen. Setiap dokumen yang diambil diproses terlebih dahulu menjadi ringkasan terstruktur sebelum diteruskan, sehingga mengurangi risiko halusinasi LLM.

**Tanggung jawab:**
- Retrieval dokumen dari knowledge base dan web
- Sintesis bukti menjadi ringkasan terstruktur
- Deduplikasi dan re-ranking sumber
- Meneruskan konteks terstruktur ke Draft Agent dan Fact-Check Pipeline

---

### 3. Draft Agent
Bertugas menyusun dan memperbaiki struktur narasi artikel berdasarkan topik atau draf awal yang diberikan.

**Tanggung jawab:**
- Menghasilkan draf artikel berstruktur (judul, lead, isi, penutup)
- Menyesuaikan panjang artikel dengan target kata
- Mengintegrasikan ringkasan bukti dari RAG Pipeline

---

### 4. Fact-Check Pipeline *(4 Sub-Agen)*
> Didasarkan pada: **FactAgent, arxiv:2506.17878 — peningkatan 12,3% Macro F1**

Proses fact-checking dipecah menjadi 4 sub-agen spesialis yang bekerja secara sekuensial:

#### 4a. Input Ingestion Agent
- Dekomposisi artikel menjadi klaim-klaim individual yang dapat diverifikasi
- Pengelompokan klaim berdasarkan topik dan prioritas verifikasi

#### 4b. Query Generation Agent
- Mengubah setiap klaim menjadi subquery pencarian yang terarah dan spesifik
- Menghasilkan variasi query untuk memaksimalkan coverage bukti

#### 4c. Evidence Retrieval Agent
- Mengambil bukti dari sumber-sumber terpercaya (jurnal, media kredibel, situs resmi)
- Menilai relevansi dan kualitas tiap sumber
- **Menggunakan OSINT Layer** untuk memperkuat verifikasi bukti (lihat bagian OSINT Integration)

#### 4c-OSINT. OSINT Layer *(Fase 4 — direncanakan)*
> Lapisan intelijen sumber terbuka yang akan memperkuat Evidence Retrieval Agent melampaui web search biasa. OSINT sengaja ditunda ke Fase 4 (*lihat ADR-0003*).

OSINT akan berfungsi sebagai **sumber data mentah** — bukan pengambil keputusan. Semua hasil OSINT akan diteruskan ke Verdict Prediction Agent untuk sintesis akhir.

| Tool OSINT *(Fase 4)* | Fungsi |
|---|---|
| **Wayback Machine API** | Verifikasi konten historis |
| **Whois / SecurityTrails** | Cek reputasi & usia domain sumber |
| **Google Reverse Image API** | Verifikasi keaslian foto/gambar |
| **GDELT Project** | Database berita global real-time |
| **CommonCrawl** | Database crawl web terbuka |
| **OpenCorporates** | Data perusahaan publik global |
| **SpiderFoot** | Analisis jejak digital entitas |

#### 4d. Verdict Prediction Agent
- Mensintesis semua bukti menjadi putusan verifikasi (benar / salah / tidak dapat diverifikasi)
- Menghasilkan penjelasan yang dapat dipahami manusia untuk tiap putusan
- Menghasilkan skor kepercayaan (0–1) per klaim

---

### 5. Editor Agent
Memperbaiki kualitas bahasa, konsistensi gaya, dan struktur kalimat sesuai pedoman redaksi.

**Tanggung jawab:**
- Koreksi tata bahasa dan ejaan
- Standarisasi gaya penulisan (EYD / AP Style)
- Penyederhanaan kalimat kompleks
- Optimasi keterbacaan (Flesch score)

---

### 6. Review & Aggregator *(Debate + Consensus)*
> Didasarkan pada: **DelphiAgent (2025) — peningkatan macF1 6,84% tanpa training tambahan**

Tidak sekadar menggabungkan output secara mekanis. Aggregator menggunakan pola *Delphi Method* di mana beberapa LLM-agent dengan perspektif berbeda memberikan penilaian independen, lalu mencapai konsensus melalui putaran debat.

**Alur:**
1. **Ronde 1 — Penilaian Independen:** Setiap agen (Draft, Fact-Check, Editor) menyampaikan penilaian terhadap artikel final secara independen
2. **Deteksi Konflik:** Sistem mendeteksi ketidaksesuaian antar output (misalnya: fakta terverifikasi bertentangan dengan klaim di draf)
3. **Ronde 2 — Debat & Sintesis:** Agen-agen berdebat pada poin konflik dan menghasilkan konsensus
4. **Output Final:** Artikel terintegrasi dengan resolusi konflik yang transparan

---

### 7. Quality Gate *(Credibility Scoring)*
> Didasarkan pada: **MAFC, Scientific Reports (2026)**

Menggantikan pendekatan lolos/gagal biner dengan sistem skor kredibilitas 0–1 yang lebih nuanced.

**Komponen skor:**
- Skor akurasi faktual (dari Fact-Check Pipeline)
- Skor konsistensi narasi (dari Editor Agent)
- Skor resolusi konflik (dari Aggregator)
- Skor kualitas sumber bukti

**Keputusan:**
- `score ≥ 0.75` → lanjut ke Publisher Agent
- `0.50 ≤ score < 0.75` → revisi parsial (kembali ke agen spesifik)
- `score < 0.50` → revisi penuh (kembali ke Orchestrator)

---

### 8. Publisher Agent
Menerima artikel final dari Quality Gate dan mempublikasikannya ke CMS sesuai jadwal.

**Tanggung jawab:**
- Upload ke CMS via REST API
- Penjadwalan waktu publikasi
- Penambahan metadata (kategori, tag, SEO)
- Notifikasi ke tim redaksi

---

## Alur Kerja

```
1. Input diterima (topik / draf mentah / URL sumber)
2. RAG Pipeline mengambil & mensintesis bukti terstruktur
3. Orchestrator mendistribusikan tugas ke agen spesialis
4. [PARALEL] Draft Agent + Fact-Check Pipeline (4 sub-agen) + Editor Agent
5. Review & Aggregator:
   a. Ronde 1: penilaian independen tiap agen
   b. Deteksi konflik antar output
   c. Ronde 2: debat & sintesis konsensus
6. Quality Gate menghitung credibility score (0–1):
   - score ≥ 0.75  → Publisher Agent
   - 0.50–0.74     → revisi parsial ke agen terkait
   - < 0.50        → revisi penuh ke Orchestrator
7. Publisher Agent mempublikasikan ke CMS
```

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Framework Multi-Agent | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM Adapter Layer** | `BaseLLMAdapter` — pluggable: Claude, GPT-4o, Gemini, Mistral, Qwen |
| LLM Default | Claude API (`claude-sonnet-4-20250514`) via `ClaudeAdapter` |
| RAG & Evidence Retrieval | Custom pipeline: Retriever → Synthesizer → Reranker (httpx + BeautifulSoup) |
| Search Provider | Tavily (default), Serper (alternatif) |
| Vector Store | PostgreSQL + pgvector (Fase 2) |
| Backend | Python 3.10+ / FastAPI / Pydantic |
| Frontend | Next.js 14 + TypeScript (Fase 2-3) |
| CMS Integration | WordPress REST API / Headless CMS |
| Database | PostgreSQL 17 (Docker) |
| Cache | Redis 7 (Docker) |
| Infrastructure | Docker + Docker Compose |
| **Resilience** | Tenacity (retry + backoff) + Circuit Breaker + DLQ |
| **State Management** | Immutable state schema + event sourcing (LangGraph) |
| **Security** | Input sanitization + prompt hardening + API rate limiting |
| **Cost Control** | Token budget per agen + tiered LLM config |
| Monitoring | LangSmith *(planned)* |
| OSINT *(Fase 4)* | Wayback Machine, Whois, GDELT, OpenCorporates |

---

## Struktur Proyek

```
borneo/
├── backend/
│   ├── newsagent/
│   │   ├── agents/
│   │   │   ├── orchestrator.py              # Koordinator utama
│   │   │   ├── draft_agent.py               # Penulisan artikel
│   │   │   ├── fact_check/
│   │   │   │   ├── input_ingestion.py       # Sub-agen: dekomposisi klaim
│   │   │   │   ├── query_generation.py      # Sub-agen: formulasi subquery
│   │   │   │   ├── evidence_retrieval.py    # Sub-agen: pengambilan bukti
│   │   │   │   └── verdict_prediction.py    # Sub-agen: sintesis putusan
│   │   │   ├── editor_agent.py              # Pengeditan bahasa & gaya
│   │   │   ├── aggregator.py                # Debate + consensus (DelphiAgent pattern)
│   │   │   ├── quality_gate.py              # Credibility scoring (MAFC pattern)
│   │   │   └── publisher_agent.py           # Publikasi ke CMS
│   │   ├── rag/
│   │   │   ├── pipeline.py                  # RAG orchestration (retrieve → rerank → synthesize)
│   │   │   ├── retriever.py                 # Document retrieval (LLM-powered search)
│   │   │   ├── synthesizer.py               # Structured evidence summarization
│   │   │   └── reranker.py                  # Source re-ranking
│   │   ├── core/
│   │   │   ├── graph.py                     # LangGraph workflow definition
│   │   │   ├── state.py                     # Immutable shared state schema
│   │   │   ├── config.py                    # Konfigurasi sistem
│   │   │   └── events.py                    # Event sourcing per langkah pipeline
│   │   ├── llm/
│   │   │   ├── base_adapter.py              # BaseLLMAdapter (abstract interface)
│   │   │   ├── claude_adapter.py            # Implementasi Claude API
│   │   │   ├── openai_adapter.py            # Implementasi OpenAI GPT-4
│   │   │   ├── gemini_adapter.py            # Implementasi Google Gemini
│   │   │   ├── mistral_adapter.py           # Implementasi Mistral AI
│   │   │   ├── qwen_adapter.py              # Implementasi Alibaba Qwen
│   │   │   └── adapter_factory.py           # Factory: baca config -> return adapter
│   │   ├── resilience/
│   │   │   ├── retry_policy.py              # Per-agen retry + backoff config
│   │   │   ├── circuit_breaker.py           # Circuit breaker pattern
│   │   │   ├── dead_letter_queue.py         # DLQ untuk artikel gagal
│   │   │   └── fallback.py                  # Fallback strategy per agen
│   │   ├── security/
│   │   │   ├── input_sanitizer.py           # Sanitasi input dari luar
│   │   │   ├── prompt_hardening.py          # Prompt injection mitigation
│   │   │   └── rate_limiter.py              # API rate limiting
│   │   ├── cost/
│   │   │   ├── token_budget.py              # Token budget per agen
│   │   │   └── cost_tracker.py              # Estimasi & tracking biaya per artikel
│   │   ├── tools/
│   │   │   ├── base.py                      # BaseTool protocol (lifecycle + metadata)
│   │   │   ├── web_search.py                # Tool pencarian web
│   │   │   ├── cms_client.py                # Klien CMS
│   │   │   ├── scoring.py                   # Credibility scoring engine
│   │   │   ├── search_factory.py            # Factory pattern untuk search provider
│   │   │   ├── search_provider.py           # Abstract search provider
│   │   │   ├── tavily_provider.py           # Tavily search implementation
│   │   │   └── serper_provider.py           # Serper search implementation
│   │   │   # osint/ — dijadwalkan fase berikutnya
│   │   ├── api/
│   │   │   └── main.py                      # FastAPI entrypoint
│   │   ├── utils/
│   │   │   └── prompt_loader.py             # Load prompt dari file .md
│   │   ├── prompts/
│   │   │   ├── aggregator_system.md
│   │   │   ├── aggregator_user.md
│   │   │   ├── draft_agent.md
│   │   │   ├── editor_agent.md
│   │   │   ├── evidence_retrieval_system.md
│   │   │   ├── evidence_retrieval_user.md
│   │   │   ├── input_ingestion_system.md
│   │   │   ├── input_ingestion_user.md
│   │   │   ├── publisher_agent.md
│   │   │   ├── quality_gate_system.md
│   │   │   ├── quality_gate_user.md
│   │   │   ├── query_generation_system.md
│   │   │   ├── query_generation_user.md
│   │   │   ├── verdict_prediction_system.md
│   │   │   ├── verdict_prediction_user.md
│   │   │   ├── _system_guard.md
│   │   │   └── _user_wrapper.md
│   │       └── tests/                           # In-package tests (261 test cases)
│   │       ├── test_agents/
│   │       ├── test_api/
│   │       ├── test_core/
│   │       ├── test_cost/
│   │       ├── test_integration/
│   │       ├── test_llm/
│   │       ├── test_rag/
│   │       ├── test_resilience/
│   │       ├── test_security/
│   │       └── test_tools/
│   ├── pyproject.toml
│   └── pyrightconfig.json
├── apps/
│   └── web/                                 # Next.js 16 + TypeScript (Fase 2 & 3)
├── packages/                                # Reserved for shared utilities
├── docs/
├── pnpm-workspace.yaml
├── pnpm-lock.yaml
└── docker-compose.yml
```

---

## Instalasi

### Prasyarat

- Python 3.10 atau lebih baru
- Docker & Docker Compose
- API Key Anthropic
- `uv` ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- Node.js 18+ (untuk pyright)

### Langkah Instalasi

```bash
# 1. Clone repositori
git clone https://github.com/YOUR_USERNAME/borneo.git
cd borneo

# 2. Install semua dependensi Python
uv sync --extra dev --directory backend

# 3. Install semua dependensi frontend
pnpm install

# 4. Salin file konfigurasi
cp .env.example .env

# 5. Isi variabel environment (lihat bagian Konfigurasi)
nano .env

# 6. Jalankan infrastruktur (PostgreSQL + Redis)
docker compose up -d

# 7. Jalankan API server
uvicorn newsagent.api.main:app --reload --app-dir backend
```

---

## Cara Penggunaan

### Via API

```python
import requests

response = requests.post("http://localhost:8000/process", json={
    "input_type": "topic",           # "topic" | "draft" | "url"
    "raw_input": "Dampak AI terhadap industri media Indonesia",
})

print(response.json())
# {
#   "article_id": "art_abc123",
#   "status": "published"
# }
```

### Via CLI *(coming soon)*

```bash
# Rencana: CLI untuk submit artikel via terminal
# python -m newsagent process \
#   --input "Gempa 6.2 SR mengguncang Sulawesi Tengah" \
#   --type topic
```

---

## Konfigurasi

Buat file `.env` di root proyek (isi sesuai `.env.example`):

```env
# === LLM API Keys (minimal Anthropic) ===
ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...          # opsional
# GEMINI_API_KEY=...             # opsional
# MISTRAL_API_KEY=...            # opsional
# QWEN_API_KEY=...               # opsional (DashScope)

# === Search Provider ===
TAVILY_API_KEY=tvly-...          # default search provider
# SERPER_API_KEY=...              # alternatif

# === CMS (WordPress REST API) ===
CMS_BASE_URL=https://yoursite.com/wp-json/wp/v2
CMS_API_KEY=

# === Database & Cache ===
DATABASE_URL=postgresql+asyncpg://newsagent:newsagent_dev@localhost:5432/newsagent
REDIS_URL=redis://localhost:6379/0

# === LLM per Agent ===
ORCHESTRATOR_LLM=claude
DRAFT_AGENT_LLM=claude
EDITOR_AGENT_LLM=claude
FACT_CHECK_LLM=claude
RAG_LLM=claude
PUBLISHER_AGENT_LLM=claude

# === Quality Gate ===
QUALITY_GATE_AUTO_PUBLISH=0.75
QUALITY_GATE_REVIEW_THRESHOLD=0.50
```

Semua variabel lain yang tidak disebut di sini (retry, circuit breaker, token budget, security threshold, OSINT) akan dikonfigurasi di Fase 4 — lihat [ROADMAP.md](./ROADMAP.md).

---

## Roadmap

Lihat [ROADMAP.md](./ROADMAP.md) untuk peta jalan lengkap pengembangan NewsAgent — dari fondasi agen hingga situs publik live, termasuk estimasi waktu dan milestone tiap fase.

---

## Kontribusi

Kontribusi sangat disambut! Silakan ikuti langkah berikut:

1. Fork repositori ini
2. Buat branch baru: `git checkout -b feat/nama-fitur`
3. Commit perubahan: `git commit -m "feat: add new feature"`
4. Push ke branch: `git push origin feat/nama-fitur`
5. Buka Pull Request

Pastikan semua test lulus sebelum membuka PR:

```bash
pytest backend/ -v
```

---



---

## Lisensi

Didistribusikan di bawah lisensi **Apache 2.0**. Lihat file `LICENSE` untuk detail lebih lanjut.
