from __future__ import annotations

from pathlib import Path
from typing import Any


def load_text_file(file_path: Path) -> str:
    """
    Load plain text file.

    TODO: Add encoding detection, error handling.
    """
    return file_path.read_text(encoding="utf-8")


def load_file(file_path: Path) -> dict[str, Any]:
    """
    Load a file and extract text content.

    TODO: Add support for:
      - PDF parsing (PyPDF2, pdfplumber)
      - DOCX parsing (python-docx)
      - Markdown parsing
      - CSV parsing
      - Image OCR (if needed)

    Returns dict with:
      - content: str
      - filename: str
      - content_type: str (inferred)
    """
    # Stub: only handles .txt files for now
    if file_path.suffix.lower() == ".txt":
        content = load_text_file(file_path)
    else:
        # Fallback: try as text
        try:
            content = load_text_file(file_path)
        except Exception:
            content = f"[Unsupported file type: {file_path.suffix}]"

    return {
        "content": content,
        "filename": file_path.name,
        "content_type": "text/plain",  # TODO: infer from extension/MIME
    }


def load_files(file_paths: list[Path]) -> list[dict[str, Any]]:
    """
    Load multiple files and return list of document dicts.
    """
    documents: list[dict[str, Any]] = []

    for fp in file_paths:
        try:
            doc = load_file(fp)
            doc["document_id"] = str(fp)  # Use path as ID for now
            documents.append(doc)
        except Exception as e:
            # Log error but continue
            documents.append(
                {
                    "content": f"[Error loading {fp.name}: {e}]",
                    "filename": fp.name,
                    "content_type": "text/plain",
                    "document_id": str(fp),
                    "error": str(e),
                }
            )

    return documents

