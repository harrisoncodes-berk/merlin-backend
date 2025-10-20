## Merlin Backend

An async FastAPI backend for an AI-powered Dungeon Master experience. It provides character creation, session-based chat with an LLM, and clean architecture layers (domains, repos, services, adapters).

## Features
- **Character management**: races, classes, backgrounds, inventories, spellcasting
- **Chat sessions**: session lifecycle, message history, assistant responses
- **LLM integration**: OpenAI client with JSON-mode support (via config), prompt orchestration
- **Clean architecture**: domains → repos → services → API
- **Observability & resilience**: tracing hooks, simple circuit breaker

## Tech Stack
- **Runtime**: Python 3.12+
- **Web**: FastAPI, Starlette, Uvicorn
- **DB**: PostgreSQL (SQLAlchemy Core, async)
- **Validation**: Pydantic v2
- **LLM**: OpenAI SDK (optional, falls back to a No-Op client)
- **Testing**: pytest, pytest-asyncio

## What It Does
Merlin Backend powers a narrative, rules-aware D&D experience with:

- **Character Creation & Sheets**
  - Compose characters from races, classes, and backgrounds.
  - Persist abilities (STR/DEX/CON/INT/WIS/CHA), skills, features, inventory, and optional spellcasting.
  - Clean domain models decoupled from transport and persistence.

- **Session-based Storytelling**
  - Per-user, per-character chat sessions with persistent message history.
  - Simple pagination and “active session” workflow.
  - Session metadata (title, settings) to seed adventures and track state.

- **Prompt Orchestration**
  - Builds a structured prompt that includes character sheet, recent conversation, and task instructions.
  - Targets JSON-only assistant responses with a clear, minimal schema.
  - Pluggable builders for standard follow-ups and combat scenes.

- **LLM Integration Layer**
  - Adapter pattern for LLM clients; current OpenAI implementation with JSON mode support.
  - Optional circuit breaker and budget hooks to control cost/latency.

- **Robust Architecture**
  - Domains (dataclasses) → Repos (SQLAlchemy) → Services (business logic) → API (FastAPI).
  - Strict Pydantic schemas at the edges; mappers convert between transport and domain.

## API Overview
Base path: `${api_v1_prefix}` (default `/api/v1`)

- Health
  - `GET /health` – service heartbeat
- Auth
  - `GET /auth/me` – returns current user (mocked via dependency in dev)
- Characters
  - `GET /characters` – list current user’s characters
- Creator
  - `GET /creator/races` – list races
  - `GET /creator/classes` – list classes
  - `GET /creator/backgrounds` – list backgrounds
  - `POST /creator/characters` – create character from a draft
- Chat
  - `GET /chat/sessions/{session_id}` – fetch a session
  - `POST /chat/sessions/active` – get or create active session
  - `GET /chat/sessions/{session_id}/history` – message history
  - `POST /chat/sessions/{session_id}/message` – send a message

## Project Structure
```text
app/
  adapters/           # External adapters (db, LLM)
  api/v1/             # FastAPI routes (versioned)
  dependencies/       # Dependency providers (auth, db)
  domains/            # Core domain models (dataclasses)
  mappers/            # Converters between schemas and domain
  models/             # SQLAlchemy table metadata
  repos/              # Data access layer
  schemas/            # Pydantic IO schemas
  services/           # Business logic (chat, character, orchestration)
```

## Why This Design
- **Maintainability**: clear boundaries and mappers make refactors low-risk.
- **Testability**: domain-first code and repo/service seams are easy to unit test.
- **Portability**: adapters isolate providers (e.g., swap LLM vendors, change DB).
