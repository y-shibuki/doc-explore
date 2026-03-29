from pydantic import BaseModel


class TagResponse(BaseModel):
    id: int
    name: str


class FileResponse(BaseModel):
    id: int
    path: str
    filename: str
    mtime: float
    size: int
    ext: str
    indexed_at: str
    tags: list[TagResponse] = []


class FileDetailResponse(FileResponse):
    preview: str = ""


class SearchResult(BaseModel):
    id: int
    path: str
    filename: str
    ext: str
    indexed_at: str
    tags: list[TagResponse] = []
    snippet: str = ""


class SearchResponse(BaseModel):
    total: int
    items: list[SearchResult]


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class ScanStatus(BaseModel):
    status: str
    started_at: str | None = None
    finished_at: str | None = None
    files_added: int = 0
    files_updated: int = 0
    files_deleted: int = 0


class ConfigResponse(BaseModel):
    scan_folders: list[str]
    target_extensions: list[str]
    db_path: str
    auto_scan_on_startup: bool
