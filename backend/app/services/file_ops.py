import subprocess
from pathlib import Path

from app.services.path_utils import wsl_to_windows


def open_file(wsl_path: str) -> None:
    win_path = wsl_to_windows(wsl_path)
    subprocess.Popen(
        ["explorer.exe", win_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def delete_file(wsl_path: str) -> None:
    Path(wsl_path).unlink()
