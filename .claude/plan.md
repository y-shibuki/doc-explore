# 計画: doc-explore

## Context

WSL上のPythonバックエンドがOneDrive配下の特定フォルダを走査し、Word/Excel/PDFのテキストをSQLite(FTS5)にインデックス化する個人用ファイル整理・全文検索ツール。FastAPI + Vite+React(TypeScript)構成。企業環境を想定したローカル完結設計。

---

## 技術スタック

### バックエンド (Python 3.12)

| ライブラリ | バージョン | 用途 |
|---|---|---|
| fastapi | 0.115.x | Web API フレームワーク |
| uvicorn | 0.34.x | ASGI サーバー |
| sqlalchemy[asyncio] | 2.0.x | ORM / DB 接続管理 |
| alembic | 1.14.x | DB マイグレーション |
| aiosqlite | 0.20.x | SQLite 非同期ドライバ (SQLAlchemy バックエンド) |
| python-docx | 1.1.x | .docx テキスト抽出 |
| openpyxl | 3.1.x | .xlsx テキスト抽出 |
| xlrd | 2.0.x | .xls テキスト抽出 |
| pdfplumber | 0.11.x | .pdf テキスト抽出 |
| pyyaml | 6.0.x | config.yaml パース |
| pydantic | 2.10.x | リクエスト/レスポンスモデル |
| ruff | 0.9.x | Linter / Formatter (dev) |
| pytest | 8.3.x | テスト (dev) |
| pytest-asyncio | 0.25.x | 非同期テスト (dev) |
| httpx | 0.28.x | テスト用 HTTP クライアント (dev) |

### フロントエンド (Node 22 LTS)

| ライブラリ | バージョン | 用途 |
|---|---|---|
| react | 19.x | UI ライブラリ |
| typescript | 5.7.x | 型システム |
| vite | 6.x | ビルドツール / 開発サーバー |
| tailwindcss | 4.x | ユーティリティ CSS |
| @tanstack/react-query | 5.x | サーバー状態管理・キャッシュ |
| react-icons | 5.x | アイコン |
| react-hot-toast | 2.x | 通知トースト |

---

## ディレクトリ構造

```
doc-explore/
├── Taskfile.yml                    # 全コマンド定義
├── config.yaml                     # スキャン対象フォルダ等の設定
├── config.yaml.example             # 設定テンプレート (git 管理)
├── .gitignore
├── CLAUDE.md
├── .claude/
│   └── plan.md
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini                     # Alembic 設定 (DB URL 等)
│   ├── alembic/
│   │   ├── env.py                      # マイグレーション実行環境
│   │   ├── script.py.mako              # リビジョンファイルテンプレート
│   │   └── versions/                   # マイグレーションファイル群
│   │       └── xxxx_initial_schema.py  # 初期スキーマ (files, file_content, tags, file_tags, scan_log)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI アプリ生成・ライフサイクル
│   │   ├── config.py               # config.yaml 読み込み・Settings クラス
│   │   ├── db.py                   # SQLAlchemy エンジン・セッション管理
│   │   ├── sa_models.py            # SQLAlchemy テーブル定義 (DeclarativeBase)
│   │   ├── models.py               # Pydantic レスポンス/リクエストモデル
│   │   ├── cli.py                  # task scan / task migrate 用 CLI エントリポイント
│   │   ├── routers/
│   │   │   ├── tree.py             # GET /api/tree
│   │   │   ├── search.py           # GET /api/search
│   │   │   ├── files.py            # GET/DELETE /api/files/{id}, POST open
│   │   │   ├── tags.py             # タグ CRUD + ファイルタグ関連付け
│   │   │   └── index.py            # POST /api/index/scan, GET /api/index/status
│   │   └── services/
│   │       ├── scanner.py          # ファイルシステム走査・差分検出
│   │       ├── extractor.py        # ファイル形式別テキスト抽出
│   │       ├── indexer.py          # DB へのインデックス書き込み・削除
│   │       ├── file_ops.py         # ファイル削除・OS で開く操作
│   │       └── path_utils.py       # WSLパス ↔ Windowsパス変換
│   └── tests/
│       ├── conftest.py
│       ├── test_extractor.py
│       ├── test_scanner.py
│       ├── test_indexer.py
│       ├── test_path_utils.py
│       └── test_api.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts              # プロキシ: /api → localhost:8000
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                 # ルートコンポーネント・2ペインレイアウト
│       ├── api/
│       │   └── client.ts           # fetch ラッパー・API 型定義
│       ├── hooks/
│       │   ├── useTree.ts          # ツリーデータ取得・展開状態管理
│       │   ├── useSearch.ts        # 検索クエリ・結果管理
│       │   ├── useTags.ts          # タグ CRUD
│       │   └── useFileActions.ts   # ファイル開く・削除
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx     # 左サイドバー (ツリー + 検索切替)
│       │   │   └── DetailPanel.tsx # 右パネル (ファイル詳細・タグ・操作)
│       │   ├── tree/
│       │   │   ├── FolderTree.tsx  # ツリールート
│       │   │   ├── TreeNode.tsx    # 個別ノード (フォルダ/ファイル)
│       │   │   └── TreeContext.tsx # ツリー展開状態の Context
│       │   ├── search/
│       │   │   ├── SearchBar.tsx   # 検索入力 + タグフィルタ
│       │   │   └── SearchResults.tsx
│       │   ├── tags/
│       │   │   ├── TagBadge.tsx
│       │   │   └── TagSelector.tsx
│       │   └── common/
│       │       ├── ConfirmDialog.tsx
│       │       └── Spinner.tsx
│       └── types/
│           └── index.ts            # 共有型定義
│
└── data/
    └── doc-explore.db              # SQLite DB (gitignore 対象)
```

---

## 主要コンポーネント・API

### API エンドポイント一覧

| メソッド | パス | 説明 |
|---|---|---|
| GET | /api/tree?path= | フォルダ内容取得（遅延ロード用） |
| GET | /api/search?q=&tags=&limit=&offset= | FTS5 全文検索（スニペット付き） |
| GET | /api/files/{id} | ファイル詳細 + テキストプレビュー |
| DELETE | /api/files/{id} | ファイル物理削除 + DB削除 |
| POST | /api/files/{id}/open | explorer.exe で開く |
| GET | /api/tags | 全タグ一覧（ファイル数付き） |
| POST | /api/tags | タグ作成 |
| PATCH | /api/tags/{id} | タグ名変更 |
| DELETE | /api/tags/{id} | タグ削除（file_tagsも削除） |
| POST | /api/files/{id}/tags | ファイルにタグ付与 |
| DELETE | /api/files/{id}/tags/{tag_id} | ファイルからタグ除去 |
| POST | /api/index/scan | 差分インデックス更新（バックグラウンド） |
| GET | /api/index/status | インデックス状態・進捗 |
| GET | /api/config | スキャン対象フォルダ一覧 |

---

## DB スキーマ

スキーマは SQLAlchemy モデル (`app/sa_models.py`) で定義し、Alembic マイグレーションで管理する。

### テーブル定義

| テーブル | 説明 |
|---|---|
| files | インデックス対象ファイルのメタ情報 |
| file_content | FTS5 仮想テーブル (全文検索用) |
| tags | タグマスタ |
| file_tags | ファイル-タグ関連付け |
| scan_log | スキャン実行履歴 |

### SQLAlchemy モデルで管理するテーブル (files, tags, file_tags, scan_log)

```python
# app/sa_models.py (概要)
class Base(DeclarativeBase): pass

class File(Base):
    __tablename__ = "files"
    id: Mapped[int]           # PK AUTOINCREMENT
    path: Mapped[str]         # UNIQUE, WSL 絶対パス
    filename: Mapped[str]
    mtime: Mapped[float]      # Unix timestamp
    size: Mapped[int]
    ext: Mapped[str]          # '.docx', '.pdf' 等
    indexed_at: Mapped[str]   # ISO 8601

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int]           # PK AUTOINCREMENT
    name: Mapped[str]         # UNIQUE

class FileTag(Base):
    __tablename__ = "file_tags"
    file_id: Mapped[int]      # FK → files.id ON DELETE CASCADE
    tag_id: Mapped[int]       # FK → tags.id ON DELETE CASCADE

class ScanLog(Base):
    __tablename__ = "scan_log"
    id: Mapped[int]
    started_at: Mapped[str]
    finished_at: Mapped[str | None]
    files_added: Mapped[int]
    files_updated: Mapped[int]
    files_deleted: Mapped[int]
    status: Mapped[str]       # 'running'|'completed'|'failed'
```

### FTS5 仮想テーブル (file_content)

FTS5 仮想テーブルは SQLAlchemy の DDL では表現できないため、Alembic マイグレーション内で `op.execute()` を使って直接 SQL で作成する。

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS file_content USING fts5(
    file_id UNINDEXED,
    text,
    tokenize='unicode61'
);
```

### DB マイグレーション管理

- **ツール**: Alembic (autogenerate 対応)
- **設定**: `backend/alembic.ini` (DB URL: `sqlite:///../data/doc-explore.db`)
- **モデル参照**: `alembic/env.py` で `app.sa_models.Base.metadata` を `target_metadata` に設定
- **注意**: FTS5 テーブルは autogenerate の対象外。変更時は手動で `op.execute()` を記述する。

**マイグレーション操作コマンド:**

```bash
task migrate              # マイグレーション実行 (alembic upgrade head)
task migrate:create       # 新規リビジョン作成 (MESSAGE="変更内容" task migrate:create)
task migrate:history      # マイグレーション履歴表示
task migrate:downgrade    # 1つ前に戻す
task db:reset             # DB 削除 → migrate で再作成
```

### PRAGMA 設定

WAL モードと外部キー制約は、マイグレーションではなく SQLAlchemy エンジンの接続イベントで設定する。

```python
# db.py
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

**FTS5 日本語検索の方針:**
- `unicode61` トークナイザを使用。日本語を1文字ずつ分割する。
- 検索クエリをダブルクォートで囲んでフレーズ検索: `"議事録"` → 隣接文字一致。
- 精度に不満な場合は `tokenize='trigram'` への変更を検討（インデックスサイズ増加）。

---

## UX フロー

### 通常ブラウズ
1. アプリ起動 → 左サイドバーにスキャンルートフォルダ一覧
2. フォルダクリック → `GET /api/tree?path=...` → 子要素展開（遅延ロード）
3. ファイルクリック → 右パネルにファイル詳細（メタ情報・タグ・テキストプレビュー）

### 検索 → ツリーへのジャンプ
1. 検索バーにキーワード入力（デバウンス 300ms）
2. `GET /api/search?q=...` → スニペット付き検索結果リスト
3. 検索結果のファイルをクリック:
   - 右パネルにファイル詳細表示
   - ツリーで該当ファイルの位置まで自動展開 + ハイライト（2秒後フェードアウト）
   - パスから階層を算出し、各階層を順番に API 呼び出して展開

### タグ付け
1. ファイル詳細パネルの [+ タグ追加] → ドロップダウンで既存タグ選択 or 新規作成
2. タグバッジの [×] → タグ除去
3. 検索バーでタグフィルタ（AND条件）

### ファイル削除
1. [削除] ボタン → 確認ダイアログ
2. 確認 → `DELETE /api/files/{id}` → ディスク削除 + DB削除
3. ツリーからノード除去 + 右パネルクリア + トースト

### インデックス更新
1. [スキャン] ボタン → `POST /api/index/scan` → バックグラウンド実行
2. 2秒ポーリングで進捗表示（`GET /api/index/status`）
3. 完了時にトースト（追加/更新/削除件数表示）

---

## 設定ファイル仕様

`config.yaml` (リポジトリには `config.yaml.example` を置き、実ファイルは `.gitignore`):

```yaml
scan_folders:
  - /mnt/c/Users/username/OneDrive/Documents
  - /mnt/c/Users/username/OneDrive/Reports

# target_extensions:  # デフォルト: [.docx, .xlsx, .xls, .pdf]
# db_path: ./data/doc-explore.db
# auto_scan_on_startup: false
# server:
#   host: 127.0.0.1
#   port: 8000
```

WSLパス → Windowsパス変換: `/mnt/c/Users/...` → `C:\Users\...`（`path_utils.py` で文字列操作、`wslpath` コマンド不使用）

---

## 依存パッケージ

### backend/pyproject.toml 主要設定

```toml
[project]
name = "doc-explore-backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "sqlalchemy[asyncio]>=2.0",
    "alembic>=1.14",
    "aiosqlite>=0.20",
    "python-docx>=1.1",
    "openpyxl>=3.1",
    "xlrd>=2.0",
    "pdfplumber>=0.11",
    "pyyaml>=6.0",
    "pydantic>=2.10",
]
[project.optional-dependencies]
dev = ["ruff>=0.9", "pytest>=8.3", "pytest-asyncio>=0.25", "httpx>=0.28"]
```

---

## 実装順序

### Phase 1: 基盤（DB + 設定 + FastAPI 骨格）
- ディレクトリ構造、pyproject.toml、Taskfile.yml
- SQLAlchemy モデル定義 (`app/sa_models.py`)
- Alembic 初期マイグレーション作成 (通常テーブル + FTS5 `op.execute()`)
- `alembic/env.py` に `target_metadata` 設定
- DB 接続管理 (`app/db.py`: エンジン・セッション・PRAGMA 設定)
- config.yaml 読み込み
- `task migrate` で DB 初期化 → `GET /api/config` で動作確認

### Phase 2: テキスト抽出 + インデックス
- `services/extractor.py`: docx/xlsx/xls/pdf 各形式の抽出
- `services/scanner.py`: フォルダ走査・差分検出（mtime比較）
- `services/indexer.py`: DB UPSERT/DELETE
- `POST /api/index/scan`（まず同期実行）

### Phase 3: 検索 + ツリーAPI
- `GET /api/search?q=...`（FTS5 + snippet）
- `GET /api/tree?path=...`（os.listdir + DB JOIN）
- `GET /api/files/{id}`
- バックグラウンドスキャン化（BackgroundTasks）

### Phase 4: ファイル操作 + タグ
- `POST /api/files/{id}/open`（explorer.exe）
- `DELETE /api/files/{id}`（物理削除）
- タグ CRUD 全エンドポイント

### Phase 5: フロントエンド基盤
- Vite + React + TypeScript + Tailwind セットアップ
- 2ペインレイアウト
- フォルダツリー（遅延ロード）

### Phase 6: フロントエンド完成
- 検索 → ツリージャンプ
- ファイル詳細パネル（開く・削除）
- タグ管理 UI
- スキャン進捗 UI

### Phase 7: 仕上げ
- エラーハンドリング統一
- `task build`（フロントエンドビルド → バックエンドで配信）
- 起動時自動スキャンオプション

---

## 検証方法

| Phase | 確認コマンド / 操作 |
|---|---|
| 1 | `task migrate` → DB 作成確認 → `task dev:backend` → `curl localhost:8000/api/config` |
| 2 | `curl -X POST localhost:8000/api/index/scan` → DB にファイル登録確認 |
| 3 | `curl "localhost:8000/api/search?q=テスト"` → 結果返却確認 |
| 4 | `curl -X POST localhost:8000/api/files/1/open` → エクスプローラで開く |
| 5 | `task dev:frontend` → ブラウザでツリー展開動作確認 |
| 6 | 検索 → ツリージャンプの E2E 動作確認 |
| 7 | `task build` → `task start` → `localhost:8000` で全機能確認 |

---

## DB 初期化・マイグレーション運用

### 初回セットアップ

```bash
task install           # 依存関係インストール (uv sync --extra dev)
cp config.yaml.example config.yaml
# config.yaml を編集
task migrate           # DB 作成 + 全マイグレーション適用
task dev               # 開発サーバー起動
```

`task migrate` は `uv run alembic upgrade head` を実行する。DB ファイルが存在しない場合、SQLite が自動的にファイルを作成し、全マイグレーションが順に適用される。

### スキーマ変更時の手順

1. `app/sa_models.py` のモデルを変更
2. `MESSAGE="変更内容" task migrate:create` で autogenerate リビジョン作成
3. 生成されたマイグレーションファイルを確認・修正 (FTS5 関連は手動追記)
4. `task migrate` で適用
5. マイグレーションファイルを git commit

### 開発サーバー起動時の DB 初期化

`task dev:backend` は Alembic マイグレーションを自動実行しない。DB が未作成の場合はエラーになるため、初回は必ず `task migrate` を先に実行すること。起動時に自動マイグレーションを行わない理由:

- 意図しないスキーマ変更を防ぐ
- マイグレーションの適用は明示的な操作として行うべき

### `task scan` (CLI) 実行時の前提

`task scan` もマイグレーション済みの DB が存在することを前提とする。DB 未作成の場合はエラーメッセージで `task migrate` の実行を促す。

### DB リセット

```bash
task db:reset    # data/doc-explore.db を削除 → task migrate で再作成
```

### テスト環境での DB セットアップ

テストでは本番 DB ファイルを使わず、インメモリ SQLite またはテンポラリファイルを使用する。

```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # FTS5 テーブルは run_sync 内で直接 SQL 実行
        await conn.execute(text(
            "CREATE VIRTUAL TABLE IF NOT EXISTS file_content "
            "USING fts5(file_id UNINDEXED, text, tokenize='unicode61')"
        ))
    async with AsyncSession(engine) as session:
        yield session
    await engine.dispose()
```

テスト環境では Alembic を経由せず `Base.metadata.create_all()` で直接テーブルを作成する。理由:

- テストの実行速度を優先
- テストごとにクリーンな DB が必要
- マイグレーション自体のテストは別途行う (マイグレーションの up/down が正常に動くことを確認)

### CI での DB セットアップ

```yaml
# CI ステップ例
- task install:backend
- task migrate          # CI 用 DB にマイグレーション適用
- task test:backend     # テスト実行 (テストは独自のインメモリ DB を使用)
- task lint:backend
```

CI ではマイグレーションの適用可能性を検証するために `task migrate` を実行する。ただしテスト自体はインメモリ DB を使うため、`task migrate` で作られた DB はテストには使われない。これにより「マイグレーションが壊れていないこと」と「アプリロジックの正しさ」を独立して検証できる。
