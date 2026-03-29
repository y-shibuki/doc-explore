from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"
_DEFAULT_EXTENSIONS = [".docx", ".xlsx", ".xls", ".pdf"]


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class Settings(BaseModel):
    scan_folders: list[str] = []
    target_extensions: list[str] = _DEFAULT_EXTENSIONS
    db_path: str = "./data/doc-explore.db"
    auto_scan_on_startup: bool = False
    server: ServerConfig = ServerConfig()


@lru_cache
def get_settings() -> Settings:
    if not _CONFIG_PATH.exists():
        return Settings()
    with _CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Settings(**data)
