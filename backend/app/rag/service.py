from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.rag.chunking import chunk_documents
from app.rag.loaders import load_files


class RAGService:
    """
    RAG service orchestrator.

    Responsibilities:
      - Load files
      - Chunk content
      - Generate embeddings
      - Store in ChromaDB
      - Retrieve top-k chunks on demand

    This is a separate module from /chat endpoint logic.
    """

    def __init__(self) -> None:
        # TODO: Initialize ChromaDB client
        # self.client = chromadb.Client(...)
        # self.collection = self.client.get_or_create_collection(...)
        pass

    def ingest_files(self, session_id: str, file_paths: list[Path]) -> dict[str, Any]:
        """
        Ingest files for a session: load, chunk, embed, store.

        Returns summary dict with counts.
        """
        # 1. Load files
        documents = load_files(file_paths)

        # 2. Chunk documents
        chunks = chunk_documents(documents)

        # 3. TODO: Generate embeddings
        # embeddings = generate_embeddings([c["content"] for c in chunks])

        # 4. TODO: Store in ChromaDB with metadata
        # self.collection.add(
        #     ids=[...],
        #     embeddings=embeddings,
        #     documents=[c["content"] for c in chunks],
        #     metadatas=[{...} for c in chunks],
        # )

        return {
            "session_id": session_id,
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "note": "RAG ingestion stub - embeddings and ChromaDB storage not implemented yet.",
        }

    def retrieve(self, session_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve top-k relevant chunks for a query.

        TODO:
          - Generate query embedding
          - Query ChromaDB with session_id filter
          - Return chunks with metadata
        """
        # Stub: return empty for now
        return []

    def clear_session(self, session_id: str) -> None:
        """
        Clear all chunks for a session.

        TODO: Delete from ChromaDB where metadata.session_id == session_id
        """
        pass

