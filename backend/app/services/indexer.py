from datetime import UTC, datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.sa_models import File, ScanLog
from app.services.extractor import extract_text
from app.services.scanner import FileInfo, scan_folders


async def run_scan(session: AsyncSession, folders: list[str], extensions: list[str]) -> ScanLog:
    now = datetime.now(UTC).isoformat()
    scan_log = ScanLog(started_at=now, status="running")
    session.add(scan_log)
    await session.flush()

    try:
        files_added, files_updated, files_deleted = await _do_scan(
            session, folders, extensions
        )
        scan_log.finished_at = datetime.now(UTC).isoformat()
        scan_log.files_added = files_added
        scan_log.files_updated = files_updated
        scan_log.files_deleted = files_deleted
        scan_log.status = "completed"
    except Exception as e:
        scan_log.finished_at = datetime.now(UTC).isoformat()
        scan_log.status = "failed"
        await session.commit()
        raise e

    await session.commit()
    return scan_log


async def _do_scan(
    session: AsyncSession, folders: list[str], extensions: list[str]
) -> tuple[int, int, int]:
    disk_files = scan_folders(folders, extensions)
    disk_map = {f.path: f for f in disk_files}

    result = await session.execute(select(File))
    db_files = {f.path: f for f in result.scalars().all()}

    files_added = 0
    files_updated = 0

    for path, info in disk_map.items():
        db_file = db_files.get(path)
        if db_file is None:
            await _insert_file(session, info)
            files_added += 1
        elif db_file.mtime != info.mtime or db_file.size != info.size:
            await _update_file(session, db_file, info)
            files_updated += 1

    deleted_paths = set(db_files.keys()) - set(disk_map.keys())
    files_deleted = len(deleted_paths)
    if deleted_paths:
        result = await session.execute(
            select(File).where(File.path.in_(deleted_paths))
        )
        for f in result.scalars().all():
            await session.execute(
                text("DELETE FROM file_content WHERE file_id = :fid"), {"fid": f.id}
            )
            await session.delete(f)

    return files_added, files_updated, files_deleted


async def _insert_file(session: AsyncSession, info: FileInfo) -> None:
    now = datetime.now(UTC).isoformat()
    f = File(
        path=info.path,
        filename=info.filename,
        mtime=info.mtime,
        size=info.size,
        ext=info.ext,
        indexed_at=now,
    )
    session.add(f)
    await session.flush()
    text_content = extract_text(info.path)
    await session.execute(
        text(
            "INSERT INTO file_content(file_id, text) VALUES (:fid, :txt)"
        ),
        {"fid": f.id, "txt": text_content},
    )


async def _update_file(session: AsyncSession, db_file: File, info: FileInfo) -> None:
    now = datetime.now(UTC).isoformat()
    db_file.mtime = info.mtime
    db_file.size = info.size
    db_file.indexed_at = now
    text_content = extract_text(info.path)
    await session.execute(
        text("DELETE FROM file_content WHERE file_id = :fid"), {"fid": db_file.id}
    )
    await session.execute(
        text("INSERT INTO file_content(file_id, text) VALUES (:fid, :txt)"),
        {"fid": db_file.id, "txt": text_content},
    )
