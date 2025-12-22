# AI Tool-Calling Chat App (Vue + FastAPI + OpenAI + ChromaDB)

A small full‑stack chat app that demonstrates:

- **Backend-enforced capability toggles** (only enabled tools are registered)
- **Single-round tool calling** (one tool-call round max; deterministic control flow)
- **RAG (Retrieval-Augmented Generation)** over uploaded files using **ChromaDB** (local persistent vector store) + **OpenAI embeddings**

## Quick architecture

- **Frontend**: Vue + Vite
- **Backend**: FastAPI (agent orchestration + tool gating + RAG)
- **Vector store**: ChromaDB (persistent on disk)
- **LLM**: OpenAI Chat Completions (with `tools`)

```text
frontend  ──HTTP──▶  backend (FastAPI)
                    ├─ tool registry (web/img/data)
                    ├─ RAG service (ChromaDB)
                    └─ OpenAI (chat + embeddings)
```

## Key backend behavior

### Agent loop (`/chat`)
Implemented in `backend/app/api/routes/chat.py`.

- Builds a system prompt describing enabled/disabled tools.
- Registers tools *only if enabled*.
- Calls OpenAI once.
- If tool calls are returned:
  - executes tools safely
  - injects tool results
  - calls OpenAI **one more time**
- Returns the assistant message + `tool_calls` logs.

### RAG flow (upload → ingest → retrieve)

- `POST /files/upload`
  - Stores files under `STORAGE_DIR/<session_id>/...`
  - Triggers ingestion: load → chunk → embed → upsert into Chroma

- Retrieval
  - When the user likely refers to uploaded docs, `/chat` calls `RAGService.retrieve()`.
  - Retrieved chunks are injected **explicitly** as a system message starting with `RAG_CONTEXT:`.

## Setup (local)

### Backend

1) Create `backend/.env` (copy from `backend/env.example`).
2) Set at least:
- `OPENAI_API_KEY=...`

### Frontend

Use `frontend/package.json` / pnpm lockfile.

## Environment variables

See `backend/env.example`.

## API endpoints

- `GET /health`
- `POST /files/upload` (multipart)
- `GET /files?session_id=...`
- `POST /chat`

## Tests

- Backend smoke test: `backend/app/tests/test_e2e_smoke.py`
  - Validates endpoint wiring without calling OpenAI.

- TODO: In 2–4 sentences, describe the user problem and how this app solves it.
- TODO: State the intended users and what “success” looks like (e.g., faster research, grounded answers from uploaded docs).

---

### 2. Architecture Overview

**High-level design goals**

- **Clear separation of concerns**
   - Frontend = UI + local state only
   - Backend = orchestration + safety + prompt construction + tool exposure
   - RAG = its own module/service (not embedded in `/chat` handler logic)

**High-level diagram (ASCII)**

```text
┌─────────────────────────┐        HTTP         ┌──────────────────────────┐
│        Frontend          │  ───────────────▶   │          Backend          │
│  Vue + shadcn/ui         │                    │  FastAPI (Orchestrator)    │
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
                    │  (ChromaDB local) │         │  (web/img/data)   │         │  Chat Completions │
                    │  - chunk/embed    │         │  - gated by opts  │         │  - tools enabled  │
                    │  - retrieve top-k │         │  - safe execution │         │  - decides calls  │
                    └──────────────────┘         └──────────────────┘         └──────────────────┘
```

**Frontend responsibilities**

- Render chat UI, message list, loading indicators, tool-call traces (if displayed).
- Own local UI state:
   - chat messages
   - session id
   - settings/toggles

- Send **full chat history + settings** on every `/chat` request.
- TODO: Document any client-side validation (e.g., file type checks) if implemented.

**Backend responsibilities**

- Orchestrate the agent loop:
   - build system prompt
   - conditionally expose tools based on settings
   - call OpenAI
   - execute tool calls safely
   - inject tool results
   - return final assistant message

- Enforce capability toggles:
   - **disabled tools are not registered**
   - system prompt includes “Do NOT call disabled tools”

- Delegate retrieval to the **RAG module** (separate module boundary).

**Where RAG lives**

- RAG logic lives in a separate module (example: `backend/rag/`), not inside `/chat` endpoint logic.
- `/chat` can *invoke* RAG retrieval via a function call, but chunking/embedding/storage/retrieval stay inside that module.

---

### 3. Technology Stack

- **Frontend**: Vue + shadcn/ui
   - TODO: Add router/state libs if used (keep minimal).

- **Backend**: FastAPI (Python)
- **LLM**: OpenAI Chat Completions with **tools**
- **RAG Vector Store**: ChromaDB (local)
- **Storage**: In-memory or local disk (session scoped)
   - TODO: Specify where sessions/files are stored.

**Non-goals**

- No heavy agent frameworks (LangChain, etc.) unless explicitly justified.

---

### 4. Chat Flow & Agent Design (CRITICAL)

#### 4.1 Chat Flow

1. User types a message in the UI.
2. Frontend sends:
   - full chat history
   - session id
   - settings/toggles

3. Backend builds the **system prompt**.
4. Backend defines **tools conditionally** (only enabled ones).
5. Model either:
   - responds normally, or
   - returns a tool call request

6. Backend executes tool call(s) safely and captures results.
7. Backend injects tool results back into the conversation.
8. Model produces the final assistant message.
9. Backend returns:
   - assistant message
   - tool call logs (minimal but present)

#### 4.2 Agent Responsibilities

- The agent **does not blindly call tools**.
- It must **respect user settings**:
   - Tools are only available if enabled.
   - System prompt explicitly forbids calling disabled tools.

- It should call tools only when they improve answer quality (e.g., retrieve docs when asked about uploaded files).

**Backend orchestration requirement**

- There is a single orchestration function (example: `orchestrate_chat()`) that:
   - reads settings
   - builds system prompt
   - defines tools conditionally
   - executes tool calls safely
   - returns final response + logs

**System prompt requirements**

- Must include:
   - tool descriptions (what each tool does, parameters, outputs)
   - enabled/disabled capability list
   - **explicit instruction**: **“Do NOT call tools that are disabled.”** (mandatory)

---

### 5. Capability Toggles (4 Features)

Frontend provides a settings popup with 4 toggles; the settings object is sent with every `/chat` request. Backend enforces these settings by controlling tool registration and by instructions in the system prompt.

#### 5.1 Web Search

- **Does**: TODO (e.g., searches the web for recent info, returns sources/snippets).
- **When enabled**:
   - Tool is registered with OpenAI.
   - Agent may call it if needed.

- **When disabled**:
   - Tool is not registered.
   - Agent must answer without web search.

#### 5.2 Image Generation

- **Does**: TODO (e.g., generates images from prompts via an image model/provider).
- **When enabled**: TODO
- **When disabled**: TODO

#### 5.3 Data Analysis

- **Does**: TODO (e.g., run simple computations, parse CSV, summarize structured data).
- **When enabled**: TODO
- **When disabled**: TODO

#### 5.4 Think Mode

- **Does**: Changes response style/verbosity/structure (no extra tools required).
- **When enabled**:
   - Agent produces longer, more structured reasoning-oriented answers (as appropriate).

- **When disabled**:
   - Agent produces concise, direct answers.

**Enforcement rules**

- Frontend: toggle UI + includes settings in every request.
- Backend: disabled tools are **not registered** + system prompt forbids calling disabled tools.

---

### 6. RAG (Retrieval-Augmented Generation)

#### Why RAG

- TODO: Explain why the base model isn’t enough for private/local documents, freshness, or accuracy.
- RAG lets the model answer using **user-uploaded documents** by retrieving relevant chunks at runtime.

#### High-level pipeline

1. User uploads one or more files.
2. Backend extracts text.
3. Backend chunks text (simple chunking to start).
4. Backend generates embeddings.
5. Backend stores vectors in **ChromaDB** with metadata:
   - session_id
   - filename
   - chunk index
   - any additional tags

6. On relevant queries:
   - backend retrieves top-k chunks from ChromaDB
   - retrieved chunks are injected into the prompt as context

#### Why ChromaDB

- Local, lightweight, simple developer experience.
- Good fit for small-to-medium demo datasets and quick iteration.

#### Scope limitations (intentional)

- Simple chunking and basic retrieval strategy (no advanced reranking initially).
- Local-only persistence (optional), session-scoped association.
- TODO: Document exact file types supported.

#### Integration rules (IMPORTANT)

- RAG is called **only when needed** (agent decision +/or heuristic).
- RAG logic is contained in its own module (example: `backend/rag/`).
- Retrieved chunks are added as a separate “context” block (not silently merged into user text).

---

### 7. Backend API Contract

#### `POST /chat`

**Request (example shape)**

- TODO: Replace with your actual Pydantic models once implemented.

```json
{
  "session_id": "optional-string-or-null",
  "messages": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help?" }
  ],
  "settings": {
    "web_search": true,
    "image_generation": false,
    "data_analysis": true,
    "think_mode": false
  }
}
```

**Response (example shape)**

```json
{
  "session_id": "server-generated-or-echoed",
  "assistant_message": { "role": "assistant", "content": "..." },
  "tool_calls": [
    {
      "name": "web_search",
      "input": { "query": "..." },
      "output_preview": "..."
    }
  ],
  "error": null
}
```

**Session ID usage**

- Session id links:
   - chat history (client-sent)
   - uploaded files
   - ChromaDB collection/metadata filtering

- TODO: Document session lifecycle (new session creation, expiration, cleanup).

**Validation & errors**

- Strict request validation via Pydantic.
- Clean, user-friendly errors (see Section 8).

---

### 8. Error Handling & Limitations

#### Errors handled (must be user-visible and graceful)

- **Missing API key**: backend returns clear message + 400/500 (choose and document).
- **File upload validation**:
   - supported file types only
   - size limits (TODO)

- **Tool failures**:
   - network errors / provider errors
   - tool timeouts (TODO)
   - invalid tool arguments from model

#### Non-production limitations (explicitly acknowledged)

- No auth / multi-tenant hardening (TODO).
- Local-only storage; not horizontally scalable (TODO).
- Limited observability (basic logs only) (TODO).
- RAG is basic; no advanced reranking or citation UI (TODO).

---

### 9. Setup & Running the Project

> TODO: Replace placeholder paths/commands with your real repo structure.

#### Prerequisites

- Node.js (version: TODO)
- Python (version: TODO)

#### Environment variables

- TODO: Add `.env.example` and list all variables here.
- Example:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (optional)
   - `CHROMA_PERSIST_DIR` (optional)

#### Backend (FastAPI)

```bash
# TODO: add exact commands
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend (Vue)

```bash
# TODO: add exact commands
cd frontend
npm install
npm run dev
```

#### Quick sanity check

- Open frontend at: TODO (e.g., `http://localhost:5173`)
- Backend health endpoint (if any): TODO

---

### 10. Future Improvements (Highly Recommended)

- **Streaming responses** (SSE/WebSockets) for better UX.
- **Persistent storage** for sessions and files (SQLite/Postgres).
- **Smarter RAG**:
   - better chunking
   - hybrid search
   - reranking
   - citations with chunk provenance

- **Real web search integration** with caching and rate limits.
- **Better UI/UX**:
   - tool call timeline
   - per-message settings
   - file management UI


