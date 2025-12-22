from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.rag.service import RAGService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    session_id: str | None = Form(default=None),
) -> dict:
    """
    Skeleton upload endpoint for RAG.

    Stores uploaded files under STORAGE_DIR/<session_id>/.
    TODO: add strict type/size validation, text extraction, chunking, embeddings, Chroma upsert.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    sid = session_id or str(uuid4())

    base = Path(settings.storage_dir).resolve()
    session_dir = base / sid
    session_dir.mkdir(parents=True, exist_ok=True)

    saved: list[dict] = []
    saved_paths: list[Path] = []
    for f in files:
        filename = os.path.basename(f.filename or "")
        if not filename:
            raise HTTPException(status_code=400, detail="File missing filename")

        # Minimal validation (expand later)
        if len(filename) > 200:
            raise HTTPException(status_code=400, detail=f"Filename too long: {filename}")

        target = session_dir / filename
        content = await f.read()
        target.write_bytes(content)
        saved_paths.append(target)

        saved.append(
            {
                "filename": filename,
                "bytes": len(content),
                "content_type": f.content_type,
            }
        )

    ingest_summary: dict | None = None
    ingest_error: str | None = None
    try:
        rag = RAGService()
        ingest_summary = rag.ingest_files(session_id=sid, file_paths=saved_paths)
    except Exception as e:
        ingest_error = f"{type(e).__name__}: {e}"

    return {
        "session_id": sid,
        "stored": saved,
        "ingest": ingest_summary,
        "ingest_error": ingest_error,
    }


@router.get("")
def list_files(session_id: str) -> dict:
    """
    Skeleton list endpoint for session files.
    """
    base = Path(settings.storage_dir).resolve()
    session_dir = base / session_id
    if not session_dir.exists():
        return {"session_id": session_id, "files": []}

    files = [
        {"filename": p.name, "bytes": p.stat().st_size}
        for p in session_dir.iterdir()
        if p.is_file()
    ]
    return {"session_id": session_id, "files": files}


