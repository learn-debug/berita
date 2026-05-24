# 📋 Changelog — NewsAgent

Semua perubahan penting pada proyek ini didokumentasikan di sini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), dan proyek ini menggunakan [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- External markdown prompt files in `newsagent/prompts/`
- `newsagent.utils.prompt_loader` utility to dynamically load prompts
- `VISION.md` — project vision, mission, and core values
- Root monorepo config: `pnpm-workspace.yaml`, `opencode.json`, root `package.json`
- `backend/newsagent/llm/deepseek_adapter.py` — DeepSeek LLM provider (OpenAI-compatible)
- `backend/newsagent/llm/hf_adapter.py` — HuggingFace Inference Provider adapter via OpenAI-compatible API
- `backend/newsagent/llm/fallback_adapter.py` — auto fallback antar provider saat quota habis (gemini→openrouter→hf)
- `backend/newsagent/memory/` — persistent memory layer with PostgreSQL + pgvector
  - `VerdictCache` — hash-based claim cache untuk FactCheck
  - `DraftMemory` — store draft+score+feedback untuk few-shot learning
- Self-improving loop: DraftAgent injects high-scoring past drafts, QualityGate saves each result
- `RateLimiter` async semaphore per-provider + minimum interval antar request
- Config HF model: 6 field `*_hf_model` per-agent (default Qwen2.5-7B-Instruct)
- Config fallback: `LLM_FALLBACK_CHAIN` env var untuk chain provider per-agent
- Per-agent `max_tokens` budget: Draft/Editor/Aggregator/Publisher/Verdict=4096, RAG/InputIngestion/QueryGen/QualityGate=1024-2048

### Changed
- Refactored all 9 core and fact-check agents' `_system_prompt()` methods to use `load_prompt()`
- Upgraded all agent prompts with advanced Prompt Engineering techniques: Chain of Thought (CoT), Few-Shot examples, and Multi-Role Debate formatting
- Restructured from flat project to pnpm monorepo: Python code moved to `backend/newsagent/`, frontend apps in `apps/`
- Updated all docs (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `ROADMAP.md`, `FRONTEND.md`, `docs/*`) to reflect monorepo structure
- `max_tokens` parameter di `BaseLLMAdapter.complete()` dan `complete_structured()` — default 2048
- `GeminiAdapter`: model default `gemini-2.0-flash` → `gemini-2.5-flash-lite` + tambah `@with_rate_limit_retry` + `RateLimiter`
- `MistralAdapter`: tambah `RateLimiter` interval 62 detik (sesuai batas free tier ~1 req/min)
- `adapter_factory.py`: refactor ekstrak `_build_single_adapter()`, dukungan `hf` provider dan fallback chain
- Prompt draft agent: dari "2-3 paragraf" → "6-10 paragraf, 500-800 kata" — artikel 4.3x lebih panjang
- `EvidenceRetrieval`: parallel search via `asyncio.gather` (runtime ~30s→2s), truncate 2000 chars/result, top 15 hasil
- `Synthesizer`: truncate tiap dokumen ke 3000 chars sebelum sintesis
- `OrchestratorAgent`: increment `revision_count` setiap pipeline dimulai
- `VerdictCache.get()`: tambah `await self._ensure()` yang terlewat
- `pyproject.toml` + `uv.lock`: update google-genai, mistralai, langgraph deps

### Fixed
- **Infinite pipeline loop**: `route_after_quality()` sekarang pakai `MAX_REVISIONS=2` — pipeline selalu selesai maksimal 2 revisi
- **Token overflow (422)**: `Aggregator` + `QualityGate` truncate article+report ke 10k chars masing-masing sebelum LLM call
- **Evidence cache crash**: `VerdictCache.get()` SQL query gagal karena `_ensure()` tidak di-await

### Docs
- Updated `docs/AGENT_GUIDE.md` to document the new external Markdown prompt structure and CoT requirement
- Updated `docs/AGENT_GUIDE.md` with memory layer documentation (katalog + self-improving loop)
- `ROADMAP.md`: tambah checklist "Article state machine + atomic claim" di Fase 2

---

## [0.3.0] — 2026-05-22

### Added
- `RAGPipeline` class in `rag/pipeline.py` — full retrieve → rerank → synthesize pipeline
- RAG node in LangGraph graph (between orchestrator and draft agent)
- `BaseTool` abstract protocol in `tools/base.py` with lifecycle (`setup`/`close`) + metadata
- `RAG_LLM` config setting in `Settings` for per-pipeline LLM selection
- `acquire()` public method on `RateLimiter` for external rate limit checks
- Pre-commit hooks config (`.pre-commit-config.yaml`) with ruff lint+format
- `pyrightconfig.json` for type checking via pyright
- 209 unit/integration tests (from 7 in v0.2.0)

### Changed
- Dev tooling: `ruff` replaces `black`/`isort`/`flake8` — single tool for lint + format
- Package manager: `uv` replaces `pip` — deterministic lock via `uv.lock`
- Python minimum version: 3.11 → 3.10
- `WebSearchTool` and `CMSClient` now extend `BaseTool` with lazy auto-setup
- `Retriever` now uses LLM-powered search query generation + web fetch
- Rate limiter: `_allow()` + manual recording refactored into single `acquire()`
- `pyproject.toml`: ruff config, uv dependency groups, setuptools package discovery

### Fixed
- `TokenBudgetExceeded` → `TokenBudgetExceededError` (ruff N818 convention)
- E501 line-too-long in all agent system prompts
- DeadLetterQueue: pyright type ignore for redis-py async types
- RetryPolicy: remove unused `ArticleState` and `Any` imports

### Docs
- `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `ROADMAP.md`, `DEPLOYMENT.md`, `TROUBLESHOOTING.md` — sync with new toolchain
- `.env.example` — add `RAG_LLM=claude`
- `docs/ARCHITECTURE.md` — add RAG node in pipeline diagram
- `docs/AGENT_GUIDE.md` — add `RAGPipeline` to agent catalog

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
- `pyproject.toml` (ruff, mypy, pytest config)
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
