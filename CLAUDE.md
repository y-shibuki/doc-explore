# doc-explore

OneDrive配下のフォルダを走査し、Word/Excel/PDFをSQLite(FTS5)にインデックス化する個人用ファイル整理・全文検索ツール。ローカル完結・企業環境対応。

## 概要

- **スキャン対象**: `config.yaml` で指定したWSLパスのフォルダ（複数可）
- **対応形式**: `.docx`, `.xlsx`, `.xls`, `.pdf`
- **検索**: FTS5全文検索 + タグフィルタ
- **UI**: フォルダツリー表示（遅延ロード）+ 検索結果→ツリージャンプ

## 構成

```
backend/    FastAPI (Python 3.12) + SQLite FTS5
frontend/   Vite + React + TypeScript + Tailwind CSS
data/       SQLite DB (gitignore対象)
config.yaml スキャン対象フォルダ設定
```

## コマンド

```bash
task install          # 全依存関係インストール
task dev              # バックエンド + フロントエンド同時起動
task dev:backend      # バックエンドのみ (port 8000)
task dev:frontend     # フロントエンドのみ (port 5173)
task scan             # インデックス更新（CLI経由）
task build            # フロントエンドビルド → バックエンドで配信
task start            # プロダクションモード起動
task test             # 全テスト実行
task lint             # 全Lint実行
```

## 開発環境セットアップ

```bash
# 1. 設定ファイルを作成
cp config.yaml.example config.yaml
# config.yaml の scan_folders を自分の OneDrive パスに変更

# 2. 依存関係インストール
task install

# 3. 開発サーバー起動
task dev
# バックエンド: http://localhost:8000
# フロントエンド: http://localhost:5173

# 4. 初回インデックス作成
task scan
# または UI の [スキャン] ボタンから実行
```

## 詳細設計

→ `.claude/plan.md` を参照
