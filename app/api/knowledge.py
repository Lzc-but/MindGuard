from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.security import require_admin
from app.services.knowledge import build_knowledge_index, build_knowledge_by_file

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    _: Annotated[dict, Depends(require_admin)] = None,
) -> dict:
    """知识库文件上传接口，增量构建知识库"""

    # 1.获取文件后缀名
    suffix = Path(file.filename).suffix.lower()

    # 2.只允许上传.txt和.md文件，其他格式直接报错
    # TODO 后续增加其他格式文件
    if suffix not in {".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only .txt/.md files are supported")
    
    # 3.拼接文件保存路径
    out = Path(settings.knowledge_path) / file.filename

    if out.exists():
            raise HTTPException(
                status_code=409,
                detail=f"File {file.filename} already exists. Please rename or delete it first."
            )
    # 4.如果目录不存在，自动创建文件夹
    out.parent.mkdir(parents=True, exist_ok=True)

    # 5.把上传的文件写入本地磁盘
    out.write_bytes(await file.read())

    build_knowledge_by_file(out)
    # 6.返回成功信息
    return {"message": "uploaded", "file": str(out)}

@router.post("/rebuild")
async def rebuild_index(_: Annotated[dict, Depends(require_admin)]) -> dict:
    """重建知识库索引接口"""
    chunks = build_knowledge_index()
    return {"message": "index rebuilt", "chunks": chunks}
