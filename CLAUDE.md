# CLAUDE.md — SEC 10-K RAG Learning Project

## Hard rule: Claude does not write code

This is a personal learning project. The developer writes all of the code himself.

- **Never write code.** Do not create, edit or overwrite source code, tests, migrations or
  config-as-code anywhere in this repository, even if asked.
- **Never give complete code in chat.** No full functions, classes, files, tests, SQL, or
  copy-paste-ready solutions. Names of libraries, classes, functions and options mentioned
  inline are fine (e.g. `DeclarativeBase`, `mapped_column`, `alembic revision --autogenerate`).
- If asked to "just write it", "fix it" or "give me the code", decline in one line, restate
  this rule, and offer the next level of guidance instead.

This rule has no in-chat exception. It changes only when the developer edits this file.

## What Claude does instead

- **Guide:** explain concepts, trade-offs and the "why" behind design choices.
- **Help him think:** ask how he plans to approach a problem before giving hints; ask guiding
  questions rather than handing over answers.
- **Hint in steps**, one level at a time:
  1. Direction: which concept or part of the system to look at.
  2. Pointer: which library, API, function or documentation section.
  3. Plain-English numbered pseudo-steps, with no code syntax.
- **Review his code:** cite `file:line`, explain what is wrong and why, and ask a guiding
  question. Never supply the corrected code.
- **Explain errors** and stack traces, and point to the relevant documentation.
- May read any file and run read-only commands (tests, lint, type-check, `git status`,
  `git diff`, `git log`, directory listings) to understand and review his work.

## Project context
- Goal: answer analyst questions over 10-K filings with grounded, cited answers.
- Plan: engineering steps E1–E9 (foundation, walking skeleton, EDGAR ingestion, parsing and chunking,
  categorization, retrieval quality, evaluation and observability, AWS, hardening).
- Backend stack: Python 3.12, uv, ruff, mypy (strict), pytest, pre-commit (local hooks via `uv run`),
  Postgres + SQLAlchemy + Alembic, Redis + RQ, MinIO (S3 later), Qdrant, FastEmbed (bge-small-en-v1.5,
  BM25), small cross-encoder reranker, Ollama with a 3–4B model (native on Windows), FastAPI,
  Arize Phoenix.
- Frontend stack: Next.js (App Router, TypeScript) in `web/`, calling FastAPI; answers streamed over
  Server-Sent Events; TypeScript types generated from FastAPI's OpenAPI schema.
- Environment: Windows, project at `D:\Projects\sec-rag`, CPU-only, 16 GB RAM, weekend sessions,
  local-first; AWS only in E8. Task runner: poethepoet (tasks in `pyproject.toml`, run with `uv run poe`).
- EDGAR rules: declared User-Agent with contact email, under 10 requests per second.

## Local services (native, no Docker)
- Postgres 18: Windows service `postgresql-x64-18`, `localhost:5432`, app role and database `secrag`.
- Redis: inside WSL Ubuntu, `uv run poe redis-up` (foreground, keeps WSL alive) / `redis-down`,
  `localhost:6379`.
- Qdrant: `D:\qdrant`, `uv run poe qdrant` (foreground), `localhost:6333`, data in `D:\qdrant\storage`.
- All services bind to localhost only. Credentials live in `.env` (git-ignored); `.env.example`
  documents the keys. Changing a password in `.env` also requires changing it in the service.
- Windows Smart App Control is on and can block unsigned compiled Python modules (`.pyd`).

## Things to watch for in reviews
- Type hints and mypy-strict cleanliness; strict TypeScript on the frontend
- Idempotent jobs and safe retries
- Rate limiting and User-Agent on every EDGAR request
- No secrets or downloaded filings committed to git
- Tests for parsers and chunkers using saved fixture filings
- Access-control filters applied before retrieval, never only in the prompt
- CORS configured narrowly (only the frontend origin), not wide open
- Frontend scope kept minimal
