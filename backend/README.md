# Backend — Developer Notes

Ringkasan teknis dan catatan developer untuk `backend/newsagent/`.

## Endpoint penting

- `POST /api/v1/articles/process` — router (`backend/newsagent/api/routers/articles.py`). Asinkron: mengembalikan `202 Accepted` dan memulai pipeline di background (task).
- `POST /process` — root app (`backend/newsagent/api/main.py`). Sinkron: menjalankan `graph.ainvoke()` dan menunggu hasil (timeout 120s).
- `GET /api/v1/articles` — list articles (filterable).
- `GET /api/v1/articles/{id}` — ambil article state.
- `PATCH /api/v1/articles/{id}` — aksi: `approve`, `reject`, `retry`.
- WebSocket: `/ws/{article_id}` — event stream untuk update pipeline.

Catatan: dokumentasi root hanya merujuk ke router `POST /api/v1/articles/process`; endpoint root `/process` memiliki perilaku berbeda (sinkron) — gunakan sesuai kebutuhan (background vs blocking).

## Konfigurasi runtime penting

- Rate limiter default: 60 permintaan per 60 detik (lihat `security/rate_limiter.py`).
- Pipeline timeout: 120 detik pada pemanggilan `graph.ainvoke()` (lihat `api/routers/articles.py` dan `api/main.py`).
- Database: PostgreSQL, tabel utama: `articles`, `article_events`, `article_claims` (lihat `database/schema.sql`).

## Adapter LLM yang tersedia

Daftar adapter di `backend/newsagent/llm/`:

- `base_adapter.py`
- `adapter_factory.py`
- `claude_adapter.py`
- `openai_adapter.py`
- `gemini_adapter.py`
- `mistral_adapter.py`
- `qwen_adapter.py`
- `hf_adapter.py`
- `deepseek_adapter.py`
- `openrouter_adapter.py`
- `fallback_adapter.py`

Jika menambahkan adapter baru, daftarkan di `adapter_factory.py` dan tambahkan konfigurasi pada `core/config.py`.

## Struktur modul / file penting (developer view)

- `agents/` — agen-agen utama: `orchestrator.py`, `draft_agent.py`, `editor_agent.py`, `aggregator.py`, `quality_gate.py`, `publisher_agent.py`, `memory_agent.py`, serta `fact_check/` (4 sub-agen).
- `llm/` — adapter LLM dan factory.
- `rag/` — pipeline RAG: `retriever.py`, `reranker.py`, `synthesizer.py`, `pipeline.py`.
- `api/` — FastAPI entrypoint, routers, event bus, dan `store.py` (persistence).
- `database/` — schema SQL dan repositori tambahan.
- `memory/` — engine memory/draft cache, verdict cache.
- `resilience/` — retry, circuit breaker, DLQ.
- `security/` — input sanitizer, prompt hardening, rate limiter.
- `tools/` — helper tools (perhatikan `ner_extractor.py`, `web_search.py`, `cms_client.py`, `scoring.py`).
- `prompts/` — prompt per agen (MD files).
- `tests/` — unit & integration tests.

## Storage / Locking

`ArticleStore` menggunakan klaim (`article_claims`) untuk mencegah pemrosesan paralel untuk `article_id` yang sama; fungsi `claim_for_processing`, `release_claim`, dan `reset_stale_processing` mengatur lifecycle klaim.

## Cara menjalankan tests lokal

Di lingkungan virtual Python proyek (`backend/.venv` aktif):

```bash
# jalankan semua test
pytest backend/newsagent/ -q

# atau hanya kumpulkan jumlah test
pytest --collect-only -q backend/newsagent/ | wc -l
```

## Catatan dokumentasi

Saya merekomendasikan agar README root merujuk file ini untuk detail developer. Jika Anda ingin, saya bisa menambahkan diagram dan contoh request/response untuk setiap endpoint.
