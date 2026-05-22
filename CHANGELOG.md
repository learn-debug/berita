# 📋 Changelog — NewsAgent

Semua perubahan penting pada proyek ini didokumentasikan di sini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), dan proyek ini menggunakan [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-05-22

### Added
- `GeminiAdapter` untuk Google Gemini 2.0 Flash (`llm/gemini_adapter.py`)
- `MistralAdapter` untuk Mistral AI (`llm/mistral_adapter.py`)
- `QwenAdapter` untuk Alibaba Qwen via DashScope (`llm/qwen_adapter.py`)
- Conditional routing di LangGraph graph (`route_after_quality`, `route_after_draft`)
- Rate limiting di API endpoint (`RateLimiter`)
- Input sanitasi di API endpoint (`InputSanitizer`)
- `.gitignore` dengan pengecualian `__pycache__`, `.venv`, `.mypy_cache`, `.pytest_cache`
- Mermaid pipeline diagrams di `docs/ARCHITECTURE.md` dan `README.md`

### Fixed
- **Fact-Check data flow**: InputIngestion sekarang menulis ke `fact_check_report["claims"]`, QueryGeneration ke `["queries"]`, EvidenceRetrieval ke `["evidence"]`, VerdictPrediction ke `["verdict"]`
- **Quality Gate score 0.0**: `compute_credibility()` sekarang dipanggil dengan argumen nyata dari evaluasi LLM (4 dimensi)
- **EvidenceRetrieval web search**: `WebSearchTool.fetch_page()` dipanggil per query, bukan hanya instantiate tanpa dipakai
- **Error handling**: Semua 10 agen + 5 LLM adapter + API endpoint punya `try/except` dengan fallback
- **PublisherAgent**: Menambahkan `_system_prompt()` yang hilang

### Changed
- `docs/ARCHITECTURE.md`: Replace `OllamaAdapter` → `MistralAdapter` + `QwenAdapter`
- `docs/AGENT_GUIDE.md`, `TROUBLESHOOTING.md`, `ROADMAP.md`, `adr/0002`: Replace Ollama references dengan Mistral/Qwen
- `README.md`: Update LLM provider list, tech stack, struktur `llm/`, konfigurasi `.env`
- `API_REFERENCE.md`: Tandai endpoint Fase 2 sebagai `(planned)`, pisahkan endpoint yang sudah ada
- `DEPLOYMENT.md`: Hapus referensi Alembic/Celery/production yang belum ada
- `CONTRIBUTING.md`: Update area prioritas kontribusi, perbaiki perintah mypy
- `pyproject.toml`: Tambah `[build-system]`, set Python 3.11 + mypy 3.11, perbaiki dependency groups

### Docs
- `AGENTS.md`, `README.md`, `ROADMAP.md`, `CONTRIBUTING.md` — sinkronisasi dengan status Fase 1

---

## [0.1.0] — 2026-05-22

### Added
- Struktur package `newsagent/` dengan semua sub-package
- `core/state.py` — Immutable State Schema (TypedDict)
- `core/config.py` — env-based config via pydantic-settings
- `core/events.py` — event log helper
- `core/graph.py` — LangGraph workflow engine (10 node pipeline)
- LLM Adapter Layer: `BaseLLMAdapter` abstraction, `ClaudeAdapter`, `OpenAIAdapter`, `adapter_factory`
- Resilience Layer: `with_retry` (tenacity), `CircuitBreaker`, `DeadLetterQueue` (Redis), `with_fallback`
- Security Layer: `InputSanitizer`, `PromptHardener`, `RateLimiter`
- Cost Control: `with_budget`, `CostTracker`
- Draft Agent — generate artikel dari topik + RAG context
- Orchestrator Agent — pipeline init & LangGraph integration
- Editor Agent — perbaiki tata bahasa & struktur
- Fact-Check Pipeline (4 sub-agen): InputIngestion → QueryGeneration → EvidenceRetrieval → VerdictPrediction
- Aggregator Agent — debate 2 ronde + consensus (DelphiAgent pattern)
- Quality Gate Agent — credibility scoring 0-1 dengan 3 routing
- Publisher Agent — finalisasi & publikasi ke CMS
- RAG Pipeline: `Retriever`, `Synthesizer`, `Reranker`
- Tools: `WebSearchTool`, `CMSClient`, scoring engine
- FastAPI entrypoint (`POST /process`)
- Docker Compose (PostgreSQL + Redis)
- `pyproject.toml` (black, isort, mypy, pytest config)
- `.env.example` dengan semua konfigurasi
- 7 unit test (semua passing)
- `AGENTS.md` — panduan agent untuk OpenCode sessions

### Research Foundation
- Integrasi referensi AI-Press (arxiv:2410.07561)
- Integrasi referensi FactAgent (arxiv:2506.17878)
- Integrasi referensi DelphiAgent (IPM, 2025)
- Integrasi referensi MAFC (Scientific Reports, 2026)
- Integrasi referensi Frontiers AI Pipeline (2025)

---

*Format entri changelog:*
*`[versi] — YYYY-MM-DD`*
*`Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`*
