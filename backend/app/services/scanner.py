import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInfo:
    path: str
    filename: str
    mtime: float
    size: int
    ext: str


def scan_folders(folders: list[str], target_extensions: list[str]) -> list[FileInfo]:
    exts = {e.lower() for e in target_extensions}
    found: list[FileInfo] = []
    for folder in folders:
        base = Path(folder)
        if not base.exists():
            continue
        for root, _dirs, files in os.walk(base):
            for name in files:
                ext = Path(name).suffix.lower()
                if ext not in exts:
                    continue
                full = Path(root) / name
                try:
                    stat = full.stat()
                except OSError:
                    continue
                found.append(
                    FileInfo(
                        path=str(full),
                        filename=name,
                        mtime=stat.st_mtime,
                        size=stat.st_size,
                        ext=ext,
                    )
                )
    return found
