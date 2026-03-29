from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import FileDetailResponse, TagResponse
from app.sa_models import File, FileTag, Tag
from app.services.file_ops import delete_file, open_file

router = APIRouter(prefix="/api/files", tags=["files"])

_PREVIEW_CHARS = 2000


@router.get("/{file_id}", response_model=FileDetailResponse)
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    f = await db.get(File, file_id)
    if f is None:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    ft_result = await db.execute(
        select(FileTag, Tag).join(Tag, FileTag.tag_id == Tag.id).where(FileTag.file_id == file_id)
    )
    tags = [TagResponse(id=tag.id, name=tag.name) for _, tag in ft_result.all()]

    preview_row = await db.execute(
        text("SELECT text FROM file_content WHERE file_id = :fid LIMIT 1"),
        {"fid": file_id},
    )
    row = preview_row.fetchone()
    preview = row.text[:_PREVIEW_CHARS] if row else ""

    return FileDetailResponse(
        id=f.id,
        path=f.path,
        filename=f.filename,
        mtime=f.mtime,
        size=f.size,
        ext=f.ext,
        indexed_at=f.indexed_at,
        tags=tags,
        preview=preview,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file_endpoint(file_id: int, db: AsyncSession = Depends(get_db)):
    f = await db.get(File, file_id)
    if f is None:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    try:
        delete_file(f.path)
    except FileNotFoundError:
        pass

    await db.execute(
        text("DELETE FROM file_content WHERE file_id = :fid"), {"fid": file_id}
    )
    await db.delete(f)
    await db.commit()


@router.post("/{file_id}/open", status_code=204)
async def open_file_endpoint(file_id: int, db: AsyncSession = Depends(get_db)):
    f = await db.get(File, file_id)
    if f is None:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    try:
        open_file(f.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
