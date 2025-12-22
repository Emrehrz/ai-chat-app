# AI Tool-Calling Chat App (Vue + FastAPI + OpenAI + ChromaDB)

This repository is a small full‑stack AI chat demo. The goal is to demonstrate **backend‑enforced capability toggles**, **single‑round tool calling**, and a simple **file upload + RAG** pipeline with a clean, minimal architecture.

## Current state (what is implemented today)

- **Backend‑enforced capability toggles**: disabled tools are **not registered at all**, so the model cannot call them.
- **Single‑round tool calling**: `POST /chat` runs at most **one tool round** (LLM → tools → LLM).
- **RAG (ChromaDB + OpenAI embeddings)**:
  - `POST /files/upload` stores files on disk.
  - If `OPENAI_API_KEY` is present, the backend chunks → embeds → persists to ChromaDB.
  - In `/chat`, a small heuristic triggers retrieval and injects context as a system message prefixed with `RAG_CONTEXT:`.
- **Tools (Implemented — stub)**:
  - `web_search`, `generate_image`, `analyze_json` exist as tools and can be called by the model, but **they do not have real integrations yet**. They return empty / summary outputs with a “not implemented” note.

---

## Architecture overview

### High-level design goals

- **Clear separation of concerns**
  - Frontend = UI + local state only (messages, session id, toggles)
  - Backend = orchestration + safety + prompt construction + tool exposure
  - RAG = its own module/service (not embedded in `/chat` handler logic)

### High-level diagram (ASCII)

```text
┌─────────────────────────┐        HTTP         ┌──────────────────────────┐
│        Frontend          │  ───────────────▶   │          Backend          │
│  Vue + Vite (UI)         │                    │  FastAPI (Orchestrator)   │
│  - UI / state            │   ◀──────────────  │  - Builds system prompt    │
│  - toggles/settings      │      JSON          │  - Registers tools         │
│  - chat history          │                    │  - Executes tool calls     │
└─────────────────────────┘                    └───────────┬───────────────┘
                                                           │
                              ┌────────────────────────────┼────────────────────────────┐
                              │                            │                            │
                              ▼                            ▼                            ▼
                    ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
                    │  RAG Module       │         │   Tool Functions  │         │   OpenAI API      │
                    │  (ChromaDB local) │         │  (web/img/data)   │         │  Chat + Embeddings│
                    │  - chunk/embed    │         │  - gated by opts  │         │  - tools enabled  │
                    │  - retrieve top-k │         │  - stub today     │         │  - decides calls  │
                    └──────────────────┘         └──────────────────┘         └──────────────────┘
```

### Frontend responsibilities

- Owns chat UI + local state (message history, session id, settings toggles).
- For every `POST /chat` request, it sends:
  - `session_id`
  - full `messages` history
  - `settings` (capability toggles)
- File upload UI currently lives in the **Chat page** (`/chat`).
- Note: the backend can return `tool_calls`, but the current UI **does not render tool logs** (it keeps them in state only).
- The dedicated `/files` page is currently a **placeholder** (stub UI).

### Backend responsibilities

- Builds a system prompt including enabled/disabled tool list.
- Registers **only enabled tools** in the OpenAI `tools` list.
- Calls OpenAI Chat Completions.
- If tool calls are returned:
  - executes tools safely
  - injects tool results into the conversation
  - calls OpenAI **one more time**
- Optionally performs RAG retrieval and injects `RAG_CONTEXT:` as a separate system message.

---

## API

### GET `/health`

- **Purpose**: health check
- **Response**:

```json
{ "status": "ok" }
```

### POST `/chat`

- **Purpose**: chat/agent orchestration (LLM + optional tools + optional RAG)
- **Request (JSON)**:

```json
{
  "session_id": null,
  "messages": [{ "role": "user", "content": "Hello" }],
  "settings": {
    "web_search": false,
    "image_generation": false,
    "data_analysis": false,
    "think_mode": false
  }
}
```

- **Response (JSON)**:

```json
{
  "session_id": "…",
  "assistant_message": { "role": "assistant", "content": "…" },
  "tool_calls": [
    {
      "name": "web_search",
      "input": { "query": "…" },
      "output_preview": "…",
      "error": null
    }
  ],
  "error": null
}
```

**Important behavior (current code)**

- If `OPENAI_API_KEY` is missing: the endpoint still returns **HTTP 200**, but `error` is set and `assistant_message` is `null`.
- Tool calling is capped to **one tool round**.

### POST `/files/upload` (multipart)

- **Purpose**: file upload + (if possible) ingest into RAG store
- **Form fields**:
  - `files`: 1..N files
  - `session_id`: optional (if missing, the backend generates one)
- **Response example**:

```json
{
  "session_id": "…",
  "stored": [{ "filename": "note.txt", "bytes": 11, "content_type": "text/plain" }],
  "ingest": { "session_id": "…", "documents_loaded": 1, "chunks_created": 1, "stored": 1 },
  "ingest_error": null
}
```

**Important behavior (current code)**

- Files are stored under `STORAGE_DIR/<session_id>/`.
- If `OPENAI_API_KEY` is missing, upload still succeeds; only `ingest_error` is set (because embeddings cannot be generated).

### GET `/files?session_id=...`

- **Purpose**: list files stored on disk for a given session
- **Response**:

```json
{
  "session_id": "…",
  "files": [{ "filename": "note.txt", "bytes": 11 }]
}
```

---

## Capability toggles (4 features)

Frontend stores toggles in `localStorage` and sends them with each `POST /chat` request. **Enforcement is in the backend** (disabled tools are not registered).

### Web Search — Implemented (stub)

- **Tool name**: `web_search`
- **Current behavior**: returns empty `results` + a “not implemented yet” note.
- **Expected later**: SerpAPI / Tavily / Bing (or similar) integration returning sources/snippets.

### Image Generation — Implemented (stub)

- **Tool name**: `generate_image`
- **Current behavior**: returns empty `images` + a “not implemented yet” note.
- **Expected later**: OpenAI Images (or another provider) integration.

### Data Analysis — Implemented (stub)

- **Tool name**: `analyze_json`
- **Current behavior**: returns `type` + a small serialized `preview` of the provided JSON-like payload.
- **Expected later**: real analysis (statistics, summaries, transformations, etc.).

### Think Mode — Prompt flag (active)

- Not a tool; it only adds a “Think mode enabled” line to the system prompt.
- Intended effect: encourage more thorough answers (model behavior).

---

## RAG (Retrieval‑Augmented Generation)

### Pipeline (current)

1. `POST /files/upload` stores files on disk.
2. Backend:
   - loads file content as “text” when possible,
   - chunks the content,
   - (if API key exists) generates embeddings,
   - persists chunks/embeddings to ChromaDB.
3. In `POST /chat`, if the last user message looks like it refers to uploaded documents, retrieval runs:
   - query embedding
   - Chroma query with `where={"session_id": session_id}`
   - inject retrieved chunks as a system message prefixed with `RAG_CONTEXT:`

### Supported file types (current)

- In practice: **.txt** and “UTF‑8 text‑like” files.
- PDF/DOCX/CSV/Markdown parsing is **not implemented yet**.

### Retrieval trigger (current)

- Simple keyword heuristic (e.g., “file”, “document”, “pdf”, “upload”, “attached”, etc.).

---

## Configuration

### Backend `.env`

Copy `backend/env.example` to `backend/.env` and fill at least:

- `OPENAI_API_KEY`

Other useful variables:

- `OPENAI_MODEL` (default: `gpt-4.1-mini`)
- `OPENAI_EMBEDDING_MODEL` (default: `text-embedding-3-small`)
- `CORS_ORIGINS` (default: `http://localhost:5173`)
- `STORAGE_DIR` (default: `./storage`)
- `CHROMA_PERSIST_DIR` (default: `./chroma`)
- `CHROMA_COLLECTION` (default: `rag_chunks`)

### Frontend env

- `VITE_API_BASE_URL` (default: `http://127.0.0.1:8000`)

---

## Prerequisites

- **Python**: 3.10+ (recommended 3.11+)
- **Node.js**: 18+ (recommended 20+)
- **pnpm**: use the version pinned by `frontend/package.json` (`packageManager`)

---

## Run locally (Windows PowerShell)

### Backend (FastAPI)

```powershell
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend (Vue + Vite)

This repo includes a `pnpm-lock.yaml`:

```powershell
cd frontend
pnpm install
pnpm dev
```

Frontend default: `http://localhost:5173` (Vite).

---

## Quick checklist

- `GET /health` → `{"status":"ok"}`
- Chat:
  - without `OPENAI_API_KEY`: `POST /chat` → HTTP 200 + `error` set
  - with key: `POST /chat` returns an assistant response (and may call enabled tools)
- Upload:
  - `POST /files/upload` stores files on disk
  - without key: `ingest_error` is set
  - with key: embeddings are generated and data is persisted to ChromaDB

---

## Tests

- Smoke test: `backend/app/tests/test_e2e_smoke.py`
  - validates route wiring without calling OpenAI
  - asserts deterministic “missing key” behavior

---

## Limitations (known)

- Web search / image generation / data analysis tools are **stub** implementations.
- Frontend does not show `tool_calls` logs in the UI.
- RAG loader/chunker is basic; PDF/DOCX parsing is missing; no citations/reranking UI.
- No auth / multi‑tenant hardening; not production‑hardened.

---

## Next steps (suggested)

- Implement real tool integrations (web search / image generation / data analysis)
- Improve RAG: better chunking + file type support (PDF/DOCX/CSV/MD) + citations/reranking
- Add a tool‑call timeline UI
- Streaming responses (SSE/WebSocket)
- Auth + rate limiting + observability