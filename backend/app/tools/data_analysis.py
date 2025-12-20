from __future__ import annotations

import json
from typing import Any


def analyze_json(data: Any) -> dict:
    """
    Stub data analysis tool.

    For now it just returns a small summary of the provided JSON-like payload.
    """
    try:
        serialized = json.dumps(data)[:5000]
    except Exception:
        serialized = "<unserializable>"

    return {
        "type": str(type(data)),
        "preview": serialized,
        "note": "data analysis is not implemented yet (stub).",
    }


