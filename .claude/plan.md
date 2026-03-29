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
| aiosqlite | 0.20.x | SQLite 非同期ドライバ |
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
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI アプリ生成・ライフサイクル
│   │   ├── config.py               # config.yaml 読み込み・Settings クラス
│   │   ├── db.py                   # DB 接続管理・マイグレーション
│   │   ├── models.py               # Pydantic レスポンス/リクエストモデル
│   │   ├── cli.py                  # task scan 用 CLI エントリポイント
│   │   ├── routers/
│   │   │   ├── tree.py             # GET /api/tree
│   │   │   ├── search.py           # GET /api/search
│   │   │   ├── files.py            # GET/DELETE /api/files/{id}, POST open
│   │   │   ├── tags.py             # タグ CRUD + ファイルタグ関連付け
│   │   │   └── index.py            # POST /api/index/scan, GET /api/index/status
│   │   ├── services/
│   │   │   ├── scanner.py          # ファイルシステム走査・差分検出
│   │   │   ├── extractor.py        # ファイル形式別テキスト抽出
│   │   │   ├── indexer.py          # DB へのインデックス書き込み・削除
│   │   │   ├── file_ops.py         # ファイル削除・OS で開く操作
│   │   │   └── path_utils.py       # WSLパス ↔ Windowsパス変換
│   │   └── sql/
│   │       └── schema.sql          # CREATE TABLE 文
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

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS files (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT    NOT NULL UNIQUE,  -- WSL 絶対パス
    filename   TEXT    NOT NULL,
    mtime      REAL    NOT NULL,         -- Unix timestamp (os.stat().st_mtime)
    size       INTEGER NOT NULL,
    ext        TEXT    NOT NULL,         -- '.docx', '.pdf' など (ドット付き小文字)
    indexed_at TEXT    NOT NULL          -- ISO 8601
);

CREATE INDEX IF NOT EXISTS idx_files_ext ON files(ext);

CREATE VIRTUAL TABLE IF NOT EXISTS file_content USING fts5(
    file_id UNINDEXED,
    text,
    tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS file_tags (
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (file_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_file_tags_tag ON file_tags(tag_id);

CREATE TABLE IF NOT EXISTS scan_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at   TEXT    NOT NULL,
    finished_at  TEXT,
    files_added  INTEGER DEFAULT 0,
    files_updated INTEGER DEFAULT 0,
    files_deleted INTEGER DEFAULT 0,
    status       TEXT    NOT NULL DEFAULT 'running'  -- 'running'|'completed'|'failed'
);
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
    "uvicorn>=0.34",
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
- DB 接続管理・スキーマ作成（schema.sql）
- config.yaml 読み込み
- `GET /api/config` で動作確認

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
| 1 | `task dev:backend` → `curl localhost:8000/api/config` |
| 2 | `curl -X POST localhost:8000/api/index/scan` → DB にファイル登録確認 |
| 3 | `curl "localhost:8000/api/search?q=テスト"` → 結果返却確認 |
| 4 | `curl -X POST localhost:8000/api/files/1/open` → エクスプローラで開く |
| 5 | `task dev:frontend` → ブラウザでツリー展開動作確認 |
| 6 | 検索 → ツリージャンプの E2E 動作確認 |
| 7 | `task build` → `task start` → `localhost:8000` で全機能確認 |
