from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.rag.chunking import chunk_documents
from app.rag.loaders import load_files

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI


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
        persist_dir = Path(settings.chroma_persist_dir).resolve()
        persist_dir.mkdir(parents=True, exist_ok=True)

        # Persistent client so data survives restarts
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Create collection if missing
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
        )

        self._openai = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._openai:
            raise RuntimeError("OPENAI_API_KEY is not configured; cannot generate embeddings.")
        if not texts:
            return []

        resp = self._openai.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
        # OpenAI returns items ordered by input
        return [d.embedding for d in resp.data]

    def ingest_files(self, session_id: str, file_paths: list[Path]) -> dict[str, Any]:
        """
        Ingest files for a session: load, chunk, embed, store.

        Returns summary dict with counts.
        """
        # 1. Load files
        documents = load_files(file_paths)

        # 2. Chunk documents
        chunks = chunk_documents(documents)

        # 3. Generate embeddings
        contents = [c["content"] for c in chunks]
        embeddings = self._embed_texts(contents)

        # 4. Store in ChromaDB with metadata
        ids: list[str] = []
        metadatas: list[dict[str, Any]] = []
        for i, c in enumerate(chunks):
            doc_id = str(c.get("document_id") or "unknown")
            chunk_index = int(c.get("chunk_index") or 0)
            ids.append(f"{session_id}:{doc_id}:{chunk_index}:{i}")

            # Chroma metadata must be str/int/float/bool (no None).
            raw_meta: dict[str, Any] = {
                "session_id": session_id,
                "document_id": doc_id,
                "filename": str(c.get("filename") or ""),
                "chunk_index": chunk_index,
                # Optional fields (only include if present)
                "start": c.get("start"),
                "end": c.get("end"),
            }
            meta = {k: v for k, v in raw_meta.items() if v is not None}
            metadatas.append(meta)

        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
            )

        return {
            "session_id": session_id,
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "stored": len(ids),
        }

    def retrieve(self, session_id: str, query: str, top_k: int = 5, filename: str | None = None) -> list[dict[str, Any]]:
        """
        Retrieve top-k relevant chunks for a query.

        Args:
            session_id: Session ID to filter chunks
            query: Query text for semantic search
            top_k: Number of chunks to retrieve
            filename: Optional filename to filter chunks by specific file

        Returns:
            List of chunk dicts with content, metadata, and distance
        """
        if not query.strip():
            return []

        top_k = max(1, min(int(top_k), 10))
        q_emb = self._embed_texts([query.strip()])[0]

        # Build where clause: always filter by session_id, optionally by filename
        where_clause: dict[str, Any] = {"session_id": session_id}
        if filename:
            where_clause["filename"] = filename

        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]

        out: list[dict[str, Any]] = []
        for doc, meta, dist in zip(docs, metas, dists):
            out.append(
                {
                    "content": doc,
                    "metadata": meta or {},
                    # Chroma distance is typically cosine distance (lower is better)
                    "distance": dist,
                }
            )
        return out

    def clear_session(self, session_id: str) -> None:
        """
        Clear all chunks for a session.

        TODO: Delete from ChromaDB where metadata.session_id == session_id
        """
        self.collection.delete(where={"session_id": session_id})

