from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import SearchResponse, SearchResult, TagResponse
from app.sa_models import File, FileTag, Tag

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    tags: list[int] = Query(default=[]),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = f'"{q}"'

    fts_rows = await db.execute(
        text(
            "SELECT file_id, snippet(file_content, 1, '<mark>', '</mark>', '…', 32) AS snip "
            "FROM file_content WHERE file_content MATCH :q "
            "ORDER BY rank LIMIT :limit OFFSET :offset"
        ),
        {"q": query, "limit": limit + len(tags) * 100, "offset": offset},
    )
    fts_results = fts_rows.fetchall()

    if not fts_results:
        return SearchResponse(total=0, items=[])

    fid_snip = {row.file_id: row.snip for row in fts_results}
    file_ids = list(fid_snip.keys())

    stmt = select(File).where(File.id.in_(file_ids))
    if tags:
        for tag_id in tags:
            stmt = stmt.where(
                File.id.in_(select(FileTag.file_id).where(FileTag.tag_id == tag_id))
            )
    result = await db.execute(stmt)
    files = result.scalars().all()

    tag_result = await db.execute(select(Tag))
    tag_map = {t.id: t for t in tag_result.scalars().all()}

    ft_result = await db.execute(
        select(FileTag).where(FileTag.file_id.in_([f.id for f in files]))
    )
    file_tags: dict[int, list[TagResponse]] = {}
    for ft in ft_result.scalars().all():
        tag = tag_map.get(ft.tag_id)
        if tag:
            file_tags.setdefault(ft.file_id, []).append(TagResponse(id=tag.id, name=tag.name))

    items = [
        SearchResult(
            id=f.id,
            path=f.path,
            filename=f.filename,
            ext=f.ext,
            indexed_at=f.indexed_at,
            tags=file_tags.get(f.id, []),
            snippet=fid_snip.get(f.id, ""),
        )
        for f in sorted(files, key=lambda x: file_ids.index(x.id))
    ]

    return SearchResponse(total=len(items), items=items[:limit])
