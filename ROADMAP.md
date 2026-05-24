# 🗺️ ROADMAP — NewsAgent

## Daftar Isi

- [Status Saat Ini](#status-saat-ini)
- [Fase 1 — Fondasi Agen](#fase-1--fondasi-agen)
- [Fase 2 — API & Dashboard Redaksi](#fase-2--api--dashboard-redaksi)
- [Fase 3 — Situs Berita Publik](#fase-3--situs-berita-publik)
- [Fase 4 — OSINT & Advanced Features](#fase-4--osint--advanced-features)
- [Timeline Estimasi](#timeline-estimasi)
- [Cara Validasi Tiap Fase](#cara-validasi-tiap-fase)
- [Keputusan yang Sudah Dibuat](#keputusan-yang-sudah-dibuat)


> Peta jalan pengembangan NewsAgent dari fondasi agen hingga situs berita publik yang berjalan otonom. Setiap fase dirancang agar dapat divalidasi sebelum lanjut ke fase berikutnya.

---

## Prinsip Roadmap Ini

Seperti membangun rumah: **fondasi dulu, baru dinding, baru atap.**

Jangan bangun dashboard sebelum agennya jalan. Jangan bangun situs publik sebelum dashboardnya stabil. Setiap fase menghasilkan sesuatu yang bisa diuji dan divalidasi secara nyata.

---

## Status Saat Ini

```
Selesai (Fase 1 — Fondasi Agen):
  ✅ Struktur proyek & package hierarchy
  ✅ Immutable State Schema (core/state.py)
  ✅ LangGraph workflow engine (core/graph.py)
  ✅ LLM Adapter Layer (Claude, OpenAI, Gemini, Mistral, Qwen + factory)
  ✅ Resilience Layer (retry, circuit breaker, DLQ, fallback)
  ✅ Security Layer (sanitizer, prompt hardening, rate limiter)
  ✅ Cost Control (token budget, cost tracker)
  ✅ Semua agen: Orchestrator, Draft, Editor, Fact-Check (4 sub-agen),
     Aggregator, Quality Gate, Publisher
  ✅ RAG Pipeline (pipeline, retriever, synthesizer, reranker)
  ✅ Tools (BaseTool, web search, CMS client, scoring)
   ✅ `backend/newsagent/api/main.py` — FastAPI entrypoint (POST /process)
  ✅ Docker Compose (PostgreSQL + Redis)
   ✅ 261 unit/integration test passing, ruff + mypy + pyright clean
   ✅ Semua agen ganti `complete()` → `complete_structured()` + JSON Schema (0 parsing error)
   ✅ Dev tooling: ruff, uv, pre-commit, pyright
```

---

## Fase 1 — Fondasi Agen
**Target: pipeline artikel berjalan end-to-end di lokal**

Ini fase paling kritis. Semua fase berikutnya bergantung pada stabilitas fase ini.

### 1.1 — Setup Proyek

```bash
Estimasi: 1-2 hari
```

- [x] Inisialisasi repo dengan struktur folder final
- [x] Setup virtual environment + `uv` + `pyproject.toml`
- [x] Konfigurasi `docker-compose.yml` (PostgreSQL + Redis)
- [x] Setup LangGraph sebagai workflow engine
- [x] Buat `core/state.py` — Immutable State Schema

**State schema adalah yang pertama dibuat.** Semua agen berbagi state ini — kalau salah desain di awal, semua agen harus diubah.

```python
# Contoh immutable state schema
class ArticleState(TypedDict):
    article_id: str
    input_type: str          # topic | draft | url
    raw_input: str
    rag_context: str         # output RAG Pipeline
    draft: str               # output Draft Agent
    fact_check_report: dict  # output Fact-Check Pipeline
    edited_draft: str        # output Editor Agent
    credibility_score: float # output Quality Gate
    status: str              # processing | review | published | failed
    events: list[dict]       # event log tiap langkah
```

---

### 1.2 — LLM Adapter Layer

```bash
Estimasi: 1 hari
```

**Dikerjakan sebelum agen manapun** — semua agen butuh ini.

- [x] `llm/base_adapter.py` — `BaseLLMAdapter` abstract class
- [x] `llm/claude_adapter.py` — implementasi Claude API
- [x] `llm/adapter_factory.py` — baca config `.env` → return adapter yang tepat
- [x] Test: ganti provider via config tanpa ubah kode agen

*Adapter lain (Gemini, Mistral, Qwen) ditambah setelahnya — interface-nya sudah siap.*

---

### 1.3 — Resilience Layer

```bash
Estimasi: 1 hari
```

**Dikerjakan sebelum agen manapun** — agen tanpa error handling itu rapuh.

- [x] `resilience/retry_policy.py` — per-agen retry + exponential backoff
- [x] `resilience/circuit_breaker.py` — stop retry jika gagal N kali berturut
- [x] `resilience/dead_letter_queue.py` — simpan artikel gagal di Redis DLQ
- [x] `resilience/fallback.py` — strategi fallback per agen (skip atau simplified)

---

### 1.4 — Security Layer

```bash
Estimasi: 1 hari
```

- [x] `security/input_sanitizer.py` — validasi & sanitasi input dari luar
- [x] `security/prompt_hardening.py` — mitigasi prompt injection
- [x] `security/rate_limiter.py` — rate limiting per IP/API key

---

### 1.5 — Cost Control

```bash
Estimasi: 0.5 hari
```

- [x] `cost/token_budget.py` — token budget per agen, alert jika melebihi
- [x] `cost/cost_tracker.py` — estimasi & log biaya per artikel

---

### 1.6 — Agen (urutan pengerjaan)

Dikerjakan dari yang paling sederhana agar ada output nyata lebih cepat.

#### Draft Agent
```bash
Estimasi: 1-2 hari | Output: artikel teks dari topik
```
- [x] `backend/newsagent/agents/draft_agent.py`
- [x] Prompt: terima topik + RAG context → hasilkan artikel berstruktur
- [x] Test: masukkan topik → lihat draf artikel keluar

#### Orchestrator Agent
```bash
Estimasi: 1 hari | Output: pipeline terhubung
```
- [x] `backend/newsagent/agents/orchestrator.py`
- [x] Integrasi ke LangGraph graph
- [x] Test: topik masuk → Draft Agent terpanggil otomatis

#### Editor Agent
```bash
Estimasi: 1 hari | Output: artikel diperbaiki tata bahasanya
```
- [x] `backend/newsagent/agents/editor_agent.py`
- [x] Prompt: terima draf → perbaiki bahasa & struktur → return artikel final
- [x] Test: draf kasar masuk → draf bersih keluar

#### RAG Pipeline
```bash
Estimasi: 2 hari | Output: konteks terstruktur dari sumber web
```
- [x] `backend/newsagent/rag/retriever.py` — ambil dokumen dari web search
- [x] `backend/newsagent/rag/synthesizer.py` — sintesis menjadi ringkasan terstruktur
- [x] `backend/newsagent/rag/reranker.py` — re-ranking sumber berdasarkan relevansi
- [x] Integrasi ke pipeline sebelum Draft Agent

#### Fact-Check Pipeline (4 sub-agen)
```bash
Estimasi: 3-4 hari | Output: laporan verifikasi per klaim
```
- [x] `backend/newsagent/agents/fact_check/input_ingestion.py`
- [x] `backend/newsagent/agents/fact_check/query_generation.py`
- [x] `backend/newsagent/agents/fact_check/evidence_retrieval.py`
- [x] `backend/newsagent/agents/fact_check/verdict_prediction.py`
- [x] Test: artikel dengan klaim faktual masuk → laporan verifikasi keluar

#### Review & Aggregator
```bash
Estimasi: 2 hari | Output: artikel final terintegrasi
```
- [x] `backend/newsagent/agents/aggregator.py` — debate + consensus
- [x] Implementasi 2 ronde: penilaian independen → deteksi konflik → sintesis
- [x] Test: output 3 agen masuk → artikel final dengan resolusi konflik keluar

#### Quality Gate
```bash
Estimasi: 1 hari | Output: credibility score + keputusan routing
```
- [x] `backend/newsagent/agents/quality_gate.py` — credibility scoring
- [x] Implementasi 3 jalur: auto-publish (≥0.75) / revisi parsial / revisi penuh
- [x] Test: artikel dengan skor berbeda → routing yang benar

#### Publisher Agent
```bash
Estimasi: 1 hari | Output: artikel tayang di CMS
```
- [x] `backend/newsagent/agents/publisher_agent.py`
- [x] Integrasi WordPress REST API
- [x] Test: artikel final masuk → tayang di CMS

---

### ✅ Milestone Fase 1
**Pipeline berjalan end-to-end:** masukkan topik → artikel tayang di CMS, semua lewat agen tanpa intervensi manual.

---

## Fase 2 — API & Dashboard Redaksi
**Target: tim redaksi bisa memantau dan review artikel via dashboard**

```bash
Estimasi total: 2-3 minggu
Status backend API ✅ — frontend dashboard belum dimulai
```

- [x] `backend/newsagent/api/main.py` — FastAPI dengan endpoint REST + WebSocket
- [x] Endpoint: `POST /api/v1/articles/process` (submit topik/draf) — async dengan EventBus
- [x] Endpoint: `GET /api/v1/articles` (daftar artikel + filter status/min_score + pagination)
- [x] Endpoint: `GET /api/v1/articles/{id}` (detail + laporan agen)
- [x] Endpoint: `PATCH /api/v1/articles/{id}` (approve/reject/retry)
- [x] WebSocket: `ws/{article_id}` (status pipeline real-time via EventBus)
- [x] `backend/newsagent/api/event_bus.py` — pub/sub untuk pipeline event
- [x] `backend/newsagent/api/store.py` — ArticleStore (masih in-memory)
- [ ] `apps/web/` — Next.js Dashboard Redaksi (TypeScript) — boilerplate exist, belum konten
- [ ] Dashboard Redaksi — halaman Pipeline (status agen real-time)
- [ ] Dashboard Redaksi — halaman Detail Artikel (fact-check report + approve)
- [ ] Dashboard Redaksi — halaman daftar artikel + filter
- [ ] Dashboard Redaksi — halaman input artikel baru
- [ ] Dashboard Redaksi — halaman pengaturan threshold
- [ ] Article state machine + atomic claim — cegah duplicate processing saat multi-worker, resume after crash, `article_id` + `revision_count` sebagai unique key

### ✅ Milestone Fase 2
**Dashboard berjalan:** editor bisa submit topik, pantau pipeline, review laporan fact-check, dan approve/tolak artikel — semua dari browser.

---

## Fase 3 — Situs Berita Publik
**Target: artikel bisa dibaca publik dengan label verifikasi faktual**

```bash
Estimasi total: 2-3 minggu
```

- [ ] `apps/web/` — Next.js (TypeScript) + headless CMS
- [ ] Halaman beranda (artikel terbaru per kategori)
- [ ] Halaman artikel (dengan label "Terverifikasi AI" + credibility score)
- [ ] Komponen FactClaimTooltip (klik klaim → lihat sumber verifikasi)
- [ ] Halaman kategori + filter
- [ ] Halaman "Tentang Sistem" (transparansi cara kerja AI)
- [ ] SEO + structured data (schema.org)
- [ ] Optimasi performa (SSG/ISR)

### ✅ Milestone Fase 3
**Situs publik live:** pembaca bisa membaca artikel, melihat badge verifikasi, dan menelusuri sumber tiap klaim yang terverifikasi.

---

## Fase 4 — OSINT & Advanced Features
**Target: verifikasi diperkuat dengan intelijen sumber terbuka**

```bash
Estimasi total: 3-4 minggu
Catatan: OSINT diparkir ke fase ini agar fase 1-3 bisa berjalan lebih cepat
```

- [ ] `tools/osint/wayback.py` — verifikasi historis klaim
- [ ] `tools/osint/whois_check.py` — kredibilitas domain sumber
- [ ] `tools/osint/reverse_image.py` — verifikasi keaslian foto
- [ ] `tools/osint/gdelt.py` — cross-check berita global
- [ ] `tools/osint/opencorporates.py` — verifikasi klaim korporat
- [ ] Integrasi ke Evidence Retrieval Agent
- [ ] Multimodal fact-checking — analisis gambar & video
- [ ] Dukungan multi-bahasa (EN, ID, AR)
- [ ] **Multi-channel Publisher** — adapter pattern untuk auto-post ke X, Telegram, LinkedIn, newsletter email setelah artikel tayang di CMS
- [ ] Caching Layer (semantic cache untuk query serupa)
- [ ] Fine-tuning model untuk gaya penulisan spesifik
- [ ] Plugin browser untuk input URL artikel

#### GraphRAG (Knowledge Graph)
- [ ] `rag/graph_extractor.py` — entity & relationship extraction dari artikel
- [ ] `rag/graph_store.py` — knowledge graph storage (PostgreSQL + pgvector)
- [ ] `rag/graph_retriever.py` — graph traversal untuk evidence retrieval
- [ ] Integrasi ke Fact-Check Pipeline — cross-reference klaim dengan graph
- [ ] Integrasi ke Situs Publik — halaman entitas, timeline, jaringan berita
- [ ] Cross-article deduplikasi entity & misinfo pattern detection

### ✅ Milestone Fase 4
**OSINT aktif + Knowledge Graph + Multi-Channel:** artikel melewati verifikasi domain, arsip historis, cross-check global, dan cross-reference knowledge graph sebelum tayang, lalu auto-publish ke multi-platform (sosial media, newsletter).

---

## Timeline Estimasi

```
Minggu 1-2   → Fase 1.1 - 1.5  (setup + fondasi teknis)
Minggu 3-5   → Fase 1.6         (coding semua agen)
Minggu 6-7   → Fase 1 testing   (integrasi + end-to-end test)
Minggu 8-10  → Fase 2           (API + Dashboard Redaksi)
Minggu 11-13 → Fase 3           (Situs Publik)
Minggu 14+   → Fase 4           (OSINT + Advanced)
```

*Estimasi ini untuk 1 developer aktif. Tim 2-3 orang bisa mempersingkat 30-40%.*

---

## Cara Validasi Tiap Fase

Sebelum lanjut ke fase berikutnya, pastikan:

| Fase | Cara Validasi |
|---|---|
| Fase 1 | Topik masuk → artikel tayang di CMS tanpa intervensi manual |
| Fase 2 | Editor bisa approve artikel dari dashboard tanpa akses langsung ke kode |
| Fase 3 | Pembaca awam bisa membaca artikel dan memahami label verifikasi |
| Fase 4 | Artikel dengan klaim palsu ditangkap oleh OSINT sebelum lolos Quality Gate |

---

## Keputusan yang Sudah Dibuat

| Keputusan | Alasan |
|---|---|
| HMAS bukan flat MAS | Kompleksitas task butuh hierarki agen |
| LangGraph bukan CrewAI | Lebih fleksibel untuk custom workflow |
| LLM Adapter dari awal | Hindari vendor lock-in |
| OSINT diparkir ke Fase 4 | Agar Fase 1-3 lebih cepat & fokus |
| Human-in-the-loop tetap ada | Artikel skor 0.50-0.74 tetap butuh review |
| Credibility score bukan biner | Lebih adil untuk artikel kompleks |
| Frontend publik pakai Next.js + TypeScript | Python dev tapi Next.js standar industri untuk SEO & interaktivitas tinggi |

---

*Roadmap ini hidup — akan diperbarui seiring perkembangan proyek.*
