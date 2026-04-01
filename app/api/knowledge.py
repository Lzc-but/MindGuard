from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.security import require_admin
from app.services.knowledge import build_knowledge_index

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    _: Annotated[dict, Depends(require_admin)] = None,
) -> dict:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only .txt/.md files are supported")
    out = Path(settings.knowledge_path) / file.filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(await file.read())
    return {"message": "uploaded", "file": str(out)}


@router.post("/rebuild")
async def rebuild_index(_: Annotated[dict, Depends(require_admin)]) -> dict:
    chunks = build_knowledge_index()
    return {"message": "index rebuilt", "chunks": chunks}
