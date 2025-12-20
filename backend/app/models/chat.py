from __future__ import annotations

from typing import Literal, Any

from pydantic import BaseModel, Field


ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseModel):
    role: ChatRole
    content: str


class ChatSettings(BaseModel):
    web_search: bool = False
    image_generation: bool = False
    data_analysis: bool = False
    think_mode: bool = False


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, description="Client-provided or previously returned session id.")
    messages: list[ChatMessage] = Field(min_length=1)
    settings: ChatSettings = Field(default_factory=ChatSettings)


class ToolCallLog(BaseModel):
    name: str
    input: dict[str, Any] | None = None
    output_preview: str | None = None
    error: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    assistant_message: ChatMessage | None = None
    tool_calls: list[ToolCallLog] = Field(default_factory=list)
    error: str | None = None


