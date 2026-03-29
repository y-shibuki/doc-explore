def wsl_to_windows(wsl_path: str) -> str:
    """WSLパスをWindowsパスに変換する。
    例: /mnt/c/Users/foo → C:\\Users\\foo
    """
    if not wsl_path.startswith("/mnt/"):
        return wsl_path
    parts = wsl_path[len("/mnt/"):].split("/", 1)
    drive = parts[0].upper() + ":"
    rest = parts[1].replace("/", "\\") if len(parts) > 1 else ""
    return drive + "\\" + rest if rest else drive + "\\"


def windows_to_wsl(win_path: str) -> str:
    """WindowsパスをWSLパスに変換する。
    例: C:\\Users\\foo → /mnt/c/Users/foo
    """
    path = win_path.replace("\\", "/")
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        rest = path[2:].lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return path
