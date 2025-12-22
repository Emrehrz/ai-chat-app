from __future__ import annotations

import json
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


def _should_use_rag(req: ChatRequest) -> bool:
    """Simple heuristic: use RAG when user likely refers to uploaded files."""
    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user:
        return False

    t = (last_user.content or "").lower()
    triggers = [
        "file",
        "files",
        "document",
        "pdf",
        "upload",
        "attached",
        "my notes",
        "these",
        "this doc",
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
        try:
            chunks = rag_service.retrieve(session_id=session_id, query=query, top_k=5)
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
            context_payload = {
                "session_id": session_id,
                "retrieved_chunks": chunks,
                "instruction": (
                    "Use these retrieved chunks as supporting context. "
                    "If they don't contain the answer, say so and ask for clarification."
                ),
            }
            messages.insert(
                1,
                {
                    "role": "system",
                    "content": "RAG_CONTEXT:\n" + json.dumps(context_payload, ensure_ascii=False),
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


