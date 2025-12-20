from __future__ import annotations

from typing import Any


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Simple text chunking strategy.

    TODO: Implement proper chunking:
      - Respect sentence boundaries
      - Handle markdown/structured content
      - Overlap handling
    """
    if not text:
        return []

    # Stub: just split by chunk_size for now
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - chunk_overlap if end < len(text) else end

    return chunks


def chunk_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Chunk a list of documents (each with 'content' field).

    Returns list of chunk dicts with metadata preserved.
    """
    all_chunks: list[dict[str, Any]] = []

    for doc in documents:
        content = doc.get("content", "")
        if not content:
            continue

        doc_chunks = chunk_text(content)
        for idx, chunk_text in enumerate(doc_chunks):
            chunk = {
                "content": chunk_text,
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "chunk_index": idx,
                "metadata": doc.get("metadata", {}),
            }
            all_chunks.append(chunk)

    return all_chunks

