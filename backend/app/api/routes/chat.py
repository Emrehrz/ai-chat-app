from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter
from openai import OpenAI

from app.core.config import settings
from app.models.chat import ChatMessage, ChatRequest, ChatResponse, ToolCallLog
from app.rag.service import RAGService
from app.tools.registry import execute_tool_call, get_enabled_tool_specs

router = APIRouter(tags=["chat"])


def _build_system_prompt(req: ChatRequest, enabled_tool_names: list[str]) -> str:
    disabled = [
        n
        for n in ["web_search", "generate_image", "analyze_json"]
        if n not in enabled_tool_names
    ]

    lines = [
        "You are a helpful assistant inside a chat app.",
        "Follow the user's request.",
        "If you use a tool, call it via the provided tool interface.",
        "Do not claim you used a tool unless you actually called it.",
        "If the user asks for a capability that is disabled, say it is disabled in Settings (do not blame model limitations).",
        "Tool transparency rules:",
        "- If a tool result indicates it is a stub / not implemented, explicitly tell the user the feature is a stub and may return empty results.",
        "- Keep this disclosure short and proceed with the best non-tool answer or ask for missing details/links.",
        "",
        f"Enabled tools: {', '.join(enabled_tool_names) if enabled_tool_names else '(none)'}",
        f"Disabled tools: {', '.join(disabled) if disabled else '(none)'}",
    ]

    if req.settings.think_mode:
        lines.extend(
            [
                "",
                "Think mode: enabled (be more thorough; still keep responses concise).",
            ]
        )

    return "\n".join(lines).strip()


def _get_session_files(session_id: str) -> list[str]:
    """Get list of filenames in the session directory."""
    if not session_id:
        return []
    
    base = Path(settings.storage_dir).resolve()
    session_dir = base / session_id
    if not session_dir.exists():
        return []
    
    return [f.name for f in session_dir.iterdir() if f.is_file()]


def _extract_filename_from_query(query: str, session_id: str) -> str | None:
    """
    Extract filename from user query by matching against session files.
    
    Returns the filename if found in the query, None otherwise.
    """
    if not query or not session_id:
        return None
    
    session_files = _get_session_files(session_id)
    if not session_files:
        return None
    
    query_lower = query.lower()
    
    # Check for exact filename matches (case-insensitive)
    for filename in session_files:
        filename_lower = filename.lower()
        # Check if filename appears in query
        if filename_lower in query_lower:
            return filename
        
        # Also check filename without extension
        filename_no_ext = Path(filename).stem.lower()
        if filename_no_ext and filename_no_ext in query_lower:
            return filename
    
    return None


def _should_use_rag(req: ChatRequest) -> bool:
    """Use RAG if session has uploaded files."""
    session_id = req.session_id
    if not session_id:
        return False
    
    # Check if session has files
    base = Path(settings.storage_dir).resolve()
    session_dir = base / session_id
    if session_dir.exists() and any(session_dir.iterdir()):
        # Session has files, always use RAG
        return True
    
    # Fallback to keyword-based detection
    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user:
        return False
    
    t = (last_user.content or "").lower()
    triggers = [
        "file", "files", "document", "pdf", "upload",
        "attached", "my notes", "these", "this doc"
    ]
    return any(k in t for k in triggers)


def orchestrate_chat(req: ChatRequest) -> ChatResponse:
    """Core agent loop: one OpenAI call + optional single tool round."""
    session_id = req.session_id or str(uuid4())

    if not settings.openai_api_key:
        return ChatResponse(
            session_id=session_id,
            assistant_message=None,
            tool_calls=[],
            error="OPENAI_API_KEY is not configured.",
        )

    client = OpenAI(api_key=settings.openai_api_key)

    tool_specs = get_enabled_tool_specs(req.settings)
    tool_map = {t.name: t for t in tool_specs}
    tools = [t.as_openai_tool() for t in tool_specs]
    enabled_tool_names = [t.name for t in tool_specs]

    system_prompt = _build_system_prompt(req, enabled_tool_names)

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        *({"role": m.role, "content": m.content} for m in req.messages),
    ]

    # Optional RAG injection (explicit, not merged into user text)
    if _should_use_rag(req):
        rag_service = RAGService()
        last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
        query = last_user.content if last_user else ""
        
        # Extract filename from query if user mentions a specific file
        filename = _extract_filename_from_query(query, session_id) if query else None
        
        try:
            chunks = rag_service.retrieve(session_id=session_id, query=query, top_k=5, filename=filename)
        except Exception as e:
            chunks = []
            # Keep model usable even if retrieval fails
            messages.insert(
                1,
                {
                    "role": "system",
                    "content": f"RAG retrieval failed and will be ignored. Error: {type(e).__name__}: {e}",
                },
            )

        if chunks:
            # Build readable RAG context format
            context_lines = [
                f"RAG_CONTEXT: Retrieved information from uploaded files (session: {session_id}):",
                "",
            ]
            
            for chunk in chunks:
                metadata = chunk.get("metadata", {})
                filename = metadata.get("filename", "unknown")
                chunk_index = metadata.get("chunk_index", 0)
                content = chunk.get("content", "")
                
                context_lines.append(f"--- Document: {filename} (chunk {chunk_index}) ---")
                context_lines.append(content)
                context_lines.append("")
            
            context_lines.append(
                "Instructions: Use the above retrieved chunks to answer the user's question. "
                "If the information is not in these chunks, clearly state that and ask for clarification."
            )
            
            messages.insert(
                1,
                {
                    "role": "system",
                    "content": "\n".join(context_lines),
                },
            )

    tool_logs: list[ToolCallLog] = []

    try:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=tools if tools else None,
        )
    except Exception as e:
        return ChatResponse(
            session_id=session_id,
            assistant_message=None,
            tool_calls=[],
            error=f"OpenAI call failed: {type(e).__name__}: {e}",
        )

    msg = resp.choices[0].message

    # One tool-call round max
    if getattr(msg, "tool_calls", None):
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            name = tc.function.name
            args_json = tc.function.arguments or "{}"
            log = ToolCallLog(name=name)
            try:
                parsed_args = json.loads(args_json) if args_json else {}
                log.input = parsed_args if isinstance(parsed_args, dict) else None

                result = execute_tool_call(tool_map=tool_map, name=name, arguments_json=args_json)
                preview = json.dumps(result, ensure_ascii=False)[:2000]
                log.output_preview = preview

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
                # Nudge the model to be transparent about stub tools (most reliable via system message).
                note = result.get("note") if isinstance(result, dict) else None
                if isinstance(note, str) and ("stub" in note.lower() or "not implemented" in note.lower()):
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                f"TOOL_NOTICE: {name} returned a stub/not-implemented result. "
                                "You must briefly disclose this to the user (e.g., 'Web search is enabled but is a stub right now'), "
                                "then continue without claiming fresh web results."
                            ),
                        }
                    )
            except Exception as e:
                log.error = f"{type(e).__name__}: {e}"
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            {"error": log.error, "tool": name}, ensure_ascii=False
                        ),
                    }
                )
            tool_logs.append(log)

        try:
            resp2 = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=tools if tools else None,
            )
            msg2 = resp2.choices[0].message
            assistant_text = (msg2.content or "").strip()
        except Exception as e:
            return ChatResponse(
                session_id=session_id,
                assistant_message=None,
                tool_calls=tool_logs,
                error=f"OpenAI follow-up after tool call failed: {type(e).__name__}: {e}",
            )
    else:
        assistant_text = (msg.content or "").strip()

    assistant = ChatMessage(role="assistant", content=assistant_text or "(empty response)")
    return ChatResponse(session_id=session_id, assistant_message=assistant, tool_calls=tool_logs, error=None)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return orchestrate_chat(req)


