from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import TagCreate, TagResponse, TagUpdate
from app.sa_models import File, FileTag, Tag

router = APIRouter(tags=["tags"])


class TagWithCount(BaseModel):
    id: int
    name: str
    file_count: int


@router.get("/api/tags", response_model=list[TagWithCount])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tag.id, Tag.name, func.count(FileTag.file_id).label("file_count"))
        .outerjoin(FileTag, Tag.id == FileTag.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    return [
        TagWithCount(id=row.id, name=row.name, file_count=row.file_count)
        for row in result.all()
    ]


@router.post("/api/tags", response_model=TagResponse, status_code=201)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="同名のタグが既に存在します")
    tag = Tag(name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagResponse(id=tag.id, name=tag.name)


@router.patch("/api/tags/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, body: TagUpdate, db: AsyncSession = Depends(get_db)):
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="タグが見つかりません")
    tag.name = body.name
    await db.commit()
    return TagResponse(id=tag.id, name=tag.name)


@router.delete("/api/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="タグが見つかりません")
    await db.delete(tag)
    await db.commit()


@router.post("/api/files/{file_id}/tags", response_model=TagResponse, status_code=201)
async def add_file_tag(
    file_id: int, body: TagCreate, db: AsyncSession = Depends(get_db)
):
    f = await db.get(File, file_id)
    if f is None:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    tag_result = await db.execute(select(Tag).where(Tag.name == body.name))
    tag = tag_result.scalar_one_or_none()
    if tag is None:
        tag = Tag(name=body.name)
        db.add(tag)
        await db.flush()

    existing = await db.execute(
        select(FileTag).where(FileTag.file_id == file_id, FileTag.tag_id == tag.id)
    )
    if existing.scalar_one_or_none() is None:
        db.add(FileTag(file_id=file_id, tag_id=tag.id))

    await db.commit()
    return TagResponse(id=tag.id, name=tag.name)


@router.delete("/api/files/{file_id}/tags/{tag_id}", status_code=204)
async def remove_file_tag(
    file_id: int, tag_id: int, db: AsyncSession = Depends(get_db)
):
    ft = await db.execute(
        select(FileTag).where(FileTag.file_id == file_id, FileTag.tag_id == tag_id)
    )
    ft_obj = ft.scalar_one_or_none()
    if ft_obj is None:
        raise HTTPException(status_code=404, detail="タグ関連付けが見つかりません")
    await db.delete(ft_obj)
    await db.commit()
