# NewsAgent — Agent Guide

## Session logging

Save to knowledge graph as `session-YYYY-MM-DD` (entityType `session`, relation `documents` to `NewsAgent`). Include work done, files changed, decisions, test counts. Do this at end of session (or when asked).

## Current state

- **Phases 1+2 complete.** HMAS backend (LangGraph, 12 agent nodes, LLM adapters, resilience/security/cost), FastAPI (REST + WebSocket), Docker Compose, Next.js 16 dashboard all exist.
- **293 tests passing** (run from `backend/`: `pytest newsagent/ -q`).
- **mypy: 17 pre-existing errors; pyright: ~44** (unresolved optional imports `spacy`, `tavily`). Not clean.
- **Frontend** at `apps/web/`: Next.js 16 App Router, shadcn/ui, Tailwind v4, Zustand, 6 pages + login + middleware.
- **pnpm monorepo** at root. `pnpm run dev --filter web` for frontend.
- **Structured output**: 6 agents use `TEXT_OUTPUT_SCHEMA` (`{"output": "string"}`), 3 use custom schemas (QualityGate, Publisher, VerdictPrediction). RAG synthesizer uses raw `complete()`. Orchestrator/memory do not call LLM directly.
- All code committed. Working tree clean.

## Authoritative docs

| File | What it covers |
|---|---|
| `GEMINI.md` | **Mandatory** AI rules: Plan-and-Solve, SRS+Reflexion, Atomic Commit, Domain Mismatch Check |
| `CONTRIBUTING.md` | Dev commands, commit conventions, code standards |
| `ROADMAP.md` | Phase plan, build order, current status |
| `docs/ARCHITECTURE.md` | Why HMAS/LangGraph, state design, pipeline design |
| `docs/AGENT_GUIDE.md` | Agent templates, patterns, debugging (576 lines) |
| `docs/adr/` | Key ADRs |
| `docs/API_REFERENCE.md` | REST + WebSocket endpoints |
| `docs/DEPLOYMENT.md` | Local dev setup, Docker, env vars |
| `docs/TROUBLESHOOTING.md` | Common errors |
| `FRONTEND.md` | Dashboard & public site specs |
| `backend/README.md` | Backend dev notes, endpoint behavior, LLM adapter list |

## Quick start

```bash
uv sync --extra dev --directory backend
pnpm install
cp .env.example .env
docker compose up -d
uvicorn newsagent.api.main:app --reload --app-dir backend     # API :8000
pnpm run dev --filter web                                       # UI :3000
```

## Commands

```bash
# backend (from project root — all use `uv run --directory backend`)
uv run --directory backend pytest newsagent/ -v -q
uv run --directory backend pytest newsagent/ -v --cov=newsagent --cov-report=term-missing
uv run --directory backend ruff check newsagent/ --fix && ruff format newsagent/
uv run --directory backend mypy newsagent/
uv run --directory backend npx --yes pyright newsagent/
uv run --directory backend pip-audit --strict --path .venv

# frontend (from project root)
pnpm run dev --filter web
pnpm build --filter web

# pre-commit
pre-commit run --all-files
pre-commit install
```

- Commit: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`).
- Test coverage target: 80% per module.

## Key architecture

- **HMAS**, not flat MAS — `OrchestratorAgent` at top, specialist agents below. LangGraph graph-based control + immutable state.
- **State is immutable** — agents return new state dict, never mutate in place. Event log is append-only.
- **LLM Adapter Pattern** — agents never call LLM directly; use `BaseLLMAdapter`. Provider per-agent via `.env` (`*_LLM=claude`).
- **12-node pipeline**: orchestrator → rag_pipeline → draft_agent → (conditional→orchestrator|editor) → editor_agent → input_ingestion → query_generation → evidence_retrieval → verdict_prediction → aggregator → quality_gate → (conditional→editor|orchestrator|memory) → memory_agent → publisher → END.
- **Fact-Check**: 4 sub-agents (InputIngestion → QueryGeneration → EvidenceRetrieval → VerdictPrediction).
- **Aggregator**: 2-round Delphi debate, not mechanical merge.
- **Quality Gate**: scores 0.0–1.0. ≥0.75 auto-publish, 0.50–0.74 editor review (max 2 revisions), <0.50 full revision (max 2 revisions).
- **Two entrypoints**: `POST /api/v1/articles/process` (async, 202) for production; `POST /process` (sync, 120s timeout) for quick testing.
- Rate limiter: 60 req/60s. Pipeline timeout: 120s.
- ArticleStore uses `article_claims` table to prevent duplicate `article_id` processing.

## Development rules

- Python 3.10+, type hints on public functions, docstrings on classes + public functions.
- Each agent: one class per file, `@with_retry` + `@with_budget`, `async def run(state) -> state`.
- Tests in `newsagent/tests/test_agents/` (unit) or `newsagent/tests/test_integration/` (integration).
- `pyproject.toml`: `testpaths = ["tests", "newsagent/tests"]`, `asyncio_mode = "strict"`. Run from `backend/`, not `newsagent/tests/`.
- No generated code / migrations yet. Alembic planned.
- Human-in-the-loop: scores 0.50–0.74 route to manual editor review.
- OSINT deferred to Phase 4 (`docs/adr/0003-osint-deferred-to-phase-4.md`). Do not implement earlier.
- Follow `GEMINI.md`: Plan-and-Solve before coding, SRS+Reflexion before output, atomic commits, domain mismatch checks.

## References

- `docs/AGENT_GUIDE.md` — agent anatomy, prompts, debugging, pre-merge checklist (576 lines)
- `docs/adr/0001-hmas-vs-flat-mas.md`
- `docs/adr/0002-llm-adapter-pattern.md`
- `docs/adr/0003-osint-deferred-to-phase-4.md`
