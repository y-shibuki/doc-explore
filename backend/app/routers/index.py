from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import ScanStatus
from app.sa_models import ScanLog
from app.services.indexer import run_scan

router = APIRouter(prefix="/api/index", tags=["index"])

_current_scan_id: int | None = None


async def _scan_background(folders: list[str], extensions: list[str]) -> None:
    from app.db import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        await run_scan(session, folders, extensions)


@router.post("/scan", response_model=ScanStatus)
async def start_scan(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanLog).where(ScanLog.status == "running").limit(1)
    )
    if result.scalar_one_or_none():
        result2 = await db.execute(
            select(ScanLog).where(ScanLog.status == "running").order_by(ScanLog.id.desc()).limit(1)
        )
        running = result2.scalar_one()
        return ScanStatus(
            status=running.status,
            started_at=running.started_at,
            finished_at=running.finished_at,
            files_added=running.files_added,
            files_updated=running.files_updated,
            files_deleted=running.files_deleted,
        )

    settings = get_settings()
    background_tasks.add_task(
        _scan_background, settings.scan_folders, settings.target_extensions
    )
    return ScanStatus(status="running")


@router.get("/status", response_model=ScanStatus)
async def get_scan_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScanLog).order_by(ScanLog.id.desc()).limit(1)
    )
    log = result.scalar_one_or_none()
    if log is None:
        return ScanStatus(status="idle")
    return ScanStatus(
        status=log.status,
        started_at=log.started_at,
        finished_at=log.finished_at,
        files_added=log.files_added,
        files_updated=log.files_updated,
        files_deleted=log.files_deleted,
    )
