# NewsAgent — Agent Guide

## Current state

- **Phase 1 complete.** `newsagent/` package, all agents, LangGraph pipeline, LLM adapters, resilience/security/cost layers, FastAPI entrypoint, Docker Compose, and tests exist and pass.
- Repo has zero commits — no code has been committed yet.

## Authoritative docs

| Doc | What it covers |
|---|---|
| `CONTRIBUTING.md` | Exact dev commands, commit conventions, code standards |
| `ROADMAP.md` | Phase plan, build order, current status |
| `docs/ARCHITECTURE.md` | Why HMAS/LangGraph, state design, pipeline design |
| `docs/AGENT_GUIDE.md` | Agent coding templates, patterns, debugging |
| `docs/adr/` | ADRs for key decisions (LLM Adapter, OSINT deferral, etc.) |
| `docs/API_REFERENCE.md` | Planned REST + WebSocket endpoints |

## Quick start

```bash
uv sync --extra dev   # install semua deps (termasuk dev)
npm install           # install pyright (type checker)
```

## Commands (via `uv run` or direct after `uv shell`)

```bash
# format & lint (replaces black, isort, flake8)
ruff check . --fix
ruff format .

# type check (two options)
mypy newsagent/
npx pyright newsagent/

# security audit
pip-audit --strict --path .venv

# test (single run or with coverage)
pytest newsagent/tests/ -v
pytest newsagent/tests/ -v --cov=newsagent --cov-report=term-missing

# run API
uvicorn newsagent.api.main:app --reload

# start services
docker compose up -d

# pre-commit (run manually or auto on git commit)
pre-commit run --all-files
pre-commit install   # aktifkan hook otomatis
```

- Commit: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`).
- Test coverage target: 80% per module.

## Key architecture (non-obvious from names)

- **HMAS**, not flat MAS — `OrchestratorAgent` at top, specialist agents below. LangGraph (not CrewAI/AutoGen) because graph-based control + immutable state.
- **State is immutable** — agents return a new state dict, never mutate in place. Event log is append-only.
- **LLM Adapter Pattern** — agents never call an LLM directly; they use `BaseLLMAdapter`. Provider chosen per-agent via config.
- **Fact-Check** is 4 sub-agents: `InputIngestion → QueryGeneration → EvidenceRetrieval → VerdictPrediction`.
- **Aggregator** runs 2-round Delphi debate, not a mechanical merge.
- **Quality Gate** scores 0.0–1.0: ≥0.75 auto-publish, 0.50–0.74 editor review, <0.50 full revision.
- **Build order matters**: State schema → LLM Adapter → Resilience → Security → Cost → Agents (Draft → Orchestrator → Editor → RAG → Fact-Check → Aggregator → Quality Gate → Publisher). See `ROADMAP.md`.

## Development rules

- Python 3.10+, type hints on all public functions, docstrings on classes + public functions.
- Each agent: one class per file, `@with_retry` + `@with_budget` decorators, implements `async def run(state) -> state`.
- Each feature needs tests in `tests/test_agents/` (unit) or `tests/test_integration/` (integration).
- No generated code, no migrations, no build artifacts yet. Alembic planned for future DB migrations.
- Human-in-the-loop: scores 0.50–0.74 must route to manual editor review.

## References to preserve

- `docs/AGENT_GUIDE.md` — full agent anatomy, prompt patterns, debugging, pre-merge checklist (525 lines).
- `docs/adr/0001-hmas-vs-flat-mas.md` — why HMAS.
- `docs/adr/0002-llm-adapter-pattern.md` — why adapter pattern.
- `docs/adr/0003-osint-deferred-to-phase-4.md` — OSINT is explicitly deferred to Phase 4; do not implement in earlier phases.
