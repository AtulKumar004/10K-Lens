# CLAUDE.md — SEC 10-K RAG Learning Project

## Architecture (read this first)
- Full plan: `docs/architecture.pdf` (SEC 10-K Analyst Assistant: components, stack, repo layout,
  ingestion and query pipelines, E1–E9 engineering steps, definitions of done).
- **The plan is a living document, not a contract.** We change designs as we learn, as we did for
  tickers (a `company_tickers` table with `ticker` as the key and an `is_active` flag, instead of
  the `companies` table in the PDF). When the code and the PDF disagree, the code and the latest
  decision in chat win. Do not "fix" the code to match the PDF without asking.
- When a decision changes the plan, record the deviation (what changed, why) in the assistant's
  memory and, if it is large, in an ADR under `docs/adr/`.

## Project context
- Goal: answer analyst questions over 10-K filings with grounded, cited answers.
- Plan: engineering steps E1–E9 (foundation, walking skeleton, EDGAR ingestion, parsing and chunking,
  categorization, retrieval quality, evaluation and observability, AWS, hardening).
- Backend stack: Python 3.12, uv, ruff, mypy (strict), pytest, pre-commit (local hooks via `uv run`),
  Postgres + SQLAlchemy + Alembic, Redis + RQ, MinIO (S3 later), Qdrant, FastEmbed (bge-small-en-v1.5,
  BM25), small cross-encoder reranker, Ollama with a 3–4B model (native on Windows), FastAPI,
  Arize Phoenix. EDGAR client uses `requests`.
- Frontend: undecided between the PDF's Streamlit test UI and a Next.js app in `web/`; confirm
  with the developer before building any UI.
- Environment: Windows, project at `D:\Projects\sec-rag`, CPU-only, 16 GB RAM, weekend sessions,
  local-first; AWS only in E8. Task runner: poethepoet (tasks in `pyproject.toml`, run with `uv run poe`).
- EDGAR rules: declared User-Agent with contact email, under 10 requests per second (target 8).

## Local services (native, no Docker)
- Postgres 18: Windows service `postgresql-x64-18`, `localhost:5432`, app role and database `secrag`.
- Redis: inside WSL Ubuntu, `uv run poe redis-up` (foreground, keeps WSL alive) / `redis-down`,
  `localhost:6379`.
- Qdrant: `D:\qdrant`, `uv run poe qdrant` (foreground), `localhost:6333`, data in `D:\qdrant\storage`.
- All services bind to localhost only. Credentials live in `.env` (git-ignored); `.env.example`
  documents the keys. Changing a password in `.env` also requires changing it in the service.
- Windows Smart App Control is on and can block unsigned compiled Python modules (`.pyd`).
- Migrations: `uv run alembic ...`; the DB URL is built from `.env` in `migrations/env.py`.

## Things to watch for in reviews
- Type hints and mypy-strict cleanliness
- Idempotent jobs and safe retries
- Rate limiting and User-Agent on every EDGAR request
- No secrets or downloaded filings committed to git
- Tests for parsers and chunkers using saved fixture filings
- Access-control filters applied before retrieval, never only in the prompt
- Frontend scope kept minimal
