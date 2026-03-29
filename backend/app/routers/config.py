from fastapi import APIRouter

from app.config import get_settings
from app.models import ConfigResponse

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
async def get_config():
    settings = get_settings()
    return ConfigResponse(
        scan_folders=settings.scan_folders,
        target_extensions=settings.target_extensions,
        db_path=settings.db_path,
        auto_scan_on_startup=settings.auto_scan_on_startup,
    )
