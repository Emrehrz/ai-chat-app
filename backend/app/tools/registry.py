from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from app.models.chat import ChatSettings
from app.tools.data_analysis import analyze_json
from app.tools.image_generation import generate_image
from app.tools.web_search import web_search


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters_schema: dict[str, Any]
    handler: Callable[..., Any]

    def as_openai_tool(self) -> dict[str, Any]:
        # OpenAI "tools" format: {"type": "function", "function": { ... }}
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


def get_enabled_tool_specs(settings: ChatSettings) -> list[ToolSpec]:
    """
    Build tool list conditionally based on settings.

    IMPORTANT: disabled tools must not be registered at all.
    """
    specs: list[ToolSpec] = []

    if settings.web_search:
        specs.append(
            ToolSpec(
                name="web_search",
                description="Search the web for up-to-date information and return a list of results.",
                parameters_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                    "additionalProperties": False,
                },
                handler=lambda query: web_search(query=query),
            )
        )

    if settings.image_generation:
        specs.append(
            ToolSpec(
                name="generate_image",
                description="Generate an image from a text prompt.",
                parameters_schema={
                    "type": "object",
                    "properties": {"prompt": {"type": "string"}},
                    "required": ["prompt"],
                    "additionalProperties": False,
                },
                handler=lambda prompt: generate_image(prompt=prompt),
            )
        )

    if settings.data_analysis:
        specs.append(
            ToolSpec(
                name="analyze_json",
                description="Analyze a JSON payload and return a summary/insights.",
                parameters_schema={
                    "type": "object",
                    "properties": {"data": {}},
                    "required": ["data"],
                    "additionalProperties": True,
                },
                handler=lambda data: analyze_json(data=data),
            )
        )

    return specs


def execute_tool_call(tool_map: dict[str, ToolSpec], name: str, arguments_json: str) -> Any:
    """
    Execute a tool call safely.
    """
    if name not in tool_map:
        raise ValueError(f"Tool not found or not enabled: {name}")

    args = json.loads(arguments_json or "{}")
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be a JSON object")

    return tool_map[name].handler(**args)


