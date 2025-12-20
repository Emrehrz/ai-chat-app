from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.models.chat import ChatMessage, ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Skeleton chat endpoint.

    TODO: Replace this stub with real orchestration:
      - build system prompt
      - register tools conditionally
      - call OpenAI
      - execute tool calls safely
      - inject tool results
    """
    session_id = req.session_id or str(uuid4())

    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    echo = last_user.content if last_user else "(no user message found)"

    assistant = ChatMessage(
        role="assistant",
        content=(
            "Stub /chat response. Backend orchestration not implemented yet.\n\n"
            f"Last user message: {echo}\n\n"
            "Next: implement agent loop + conditional tools + RAG retrieval."
        ),
    )

    return ChatResponse(
        session_id=session_id,
        assistant_message=assistant,
        tool_calls=[],
        error=None,
    )


