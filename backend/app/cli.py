import asyncio
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <command>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "scan":
        asyncio.run(_scan())
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


async def _scan() -> None:
    from app.config import get_settings
    from app.db import check_db_initialized, get_session_factory
    from app.services.indexer import run_scan

    if not await check_db_initialized():
        print(
            "エラー: DB が初期化されていません。先に 'task migrate' を実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    settings = get_settings()
    factory = get_session_factory()
    async with factory() as session:
        log = await run_scan(session, settings.scan_folders, settings.target_extensions)

    print(
        f"スキャン完了: 追加={log.files_added} 更新={log.files_updated} 削除={log.files_deleted}"
    )


if __name__ == "__main__":
    main()
