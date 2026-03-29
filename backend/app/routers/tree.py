import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.sa_models import File

router = APIRouter(prefix="/api/tree", tags=["tree"])


class TreeNode(BaseModel):
    name: str
    path: str
    type: str
    file_id: int | None = None
    ext: str | None = None
    has_children: bool = False


@router.get("", response_model=list[TreeNode])
async def get_tree(
    path: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()

    if path is None:
        return [
            TreeNode(
                name=Path(folder).name or folder,
                path=folder,
                type="folder",
                has_children=True,
            )
            for folder in settings.scan_folders
        ]

    target = Path(path)
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="フォルダが見つかりません")

    result = await db.execute(select(File))
    indexed_paths = {f.path: f for f in result.scalars().all()}

    nodes: list[TreeNode] = []
    try:
        entries = sorted(os.scandir(target), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return []

    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            has_children = False
            try:
                has_children = any(True for _ in os.scandir(entry.path))
            except PermissionError:
                pass
            nodes.append(
                TreeNode(
                    name=entry.name,
                    path=entry.path,
                    type="folder",
                    has_children=has_children,
                )
            )
        elif entry.is_file():
            ext = Path(entry.name).suffix.lower()
            if ext not in settings.target_extensions:
                continue
            f = indexed_paths.get(entry.path)
            nodes.append(
                TreeNode(
                    name=entry.name,
                    path=entry.path,
                    type="file",
                    file_id=f.id if f else None,
                    ext=ext,
                )
            )

    return nodes
