# MarkItDown - ウェブサイトクローラー＆変換アプリケーション (バックエンド)

![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MarkItDown](https://img.shields.io/badge/MarkItDown-0.1.0-orange)

## 📖 概要

MarkItDownは、ウェブサイトのURLを入力すると、そのサイトをクローリング・スクレイピングし、Markdown形式に変換するWebアプリケーションのバックエンドAPIです。FastAPIで構築されており、非同期処理によって効率的なクローリングと変換を実現しています。

## ✨ 機能

- ウェブサイトのURL入力によるクローリング
- クロール深度と画像取得オプションのカスタマイズ
- 非同期処理による効率的なデータ取得
- MarkItDownライブラリを使用したMarkdown変換
- タスクベースの処理とステータス管理
- RESTful APIインターフェース

## 🛠️ 技術スタック

- **FastAPI**: 高速なPythonウェブフレームワーク
- **Pydantic**: データバリデーション
- **MarkItDown**: Markdown変換ライブラリ
- **BeautifulSoup/lxml**: スクレイピングライブラリ
- **HTTPX**: 非同期HTTPクライアント
- **Uvicorn**: ASGIサーバー

## 🚀 セットアップ方法

### 前提条件

- Python 3.10以上
- pip (Pythonパッケージマネージャー)

### インストール

1. リポジトリをクローンする:

```bash
git clone https://github.com/your-username/markitdown-backend.git
cd markitdown-backend
```

2. 仮想環境を作成してアクティベートする:

```bash
python -m venv venv
# Windowsの場合
venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate
```

3. 依存関係をインストールする:

```bash
pip install -r api/requirements.txt
```

4. 環境変数の設定:

`.env.example` ファイルを `.env` にコピーして適切な値を設定します:

```bash
cp .env.example .env
```

5. APIサーバーを起動する:

```bash
cd api
python run_server.py
```

サーバーは http://localhost:8000 で起動し、APIドキュメントは http://localhost:8000/docs で確認できます。

## 🧩 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `MAX_CRAWL_DEPTH` | 最大クロール深度 | `5` |
| `ALLOWED_ORIGINS` | CORS許可オリジン (カンマ区切り) | `*` |

## 📁 プロジェクト構造

```
/api
├── __init__.py          # パッケージ初期化
├── main.py              # FastAPIアプリケーションのメインファイル
├── models.py            # Pydanticモデル (データ検証)
├── converter.py         # Markdown変換クラス
├── crawler.py           # ウェブクローラークラス
├── tasks.py             # タスク管理システム
├── requirements.txt     # 依存関係リスト
└── run_server.py        # 開発サーバー起動スクリプト
```

## 📡 API エンドポイント

| エンドポイント | メソッド | 説明 |
|----------------|--------|------|
| `/` | GET | APIの概要情報 |
| `/api/convert/` | POST | 変換処理を開始する |
| `/api/tasks/{task_id}/` | GET | タスクのステータスを取得する |
| `/api/tasks/{task_id}/result/` | GET | 変換結果を取得する |

## 🌐 Vercelへのデプロイ

このバックエンドは[Vercel Serverless Functions](https://vercel.com/docs/serverless-functions/introduction)としてデプロイすることができます:

1. [Vercel](https://vercel.com) にアクセスしてアカウントを作成します（まだの場合）
2. 新しいプロジェクトを作成し、GitHubリポジトリと連携します
3. 必要な環境変数を設定します
4. デプロイを開始します

Vercelのデプロイには以下のファイルが重要です:
- `vercel.json`: Vercel設定ファイル（環境変数、ルート設定など）
- `api/requirements.txt`: 必要なPythonパッケージ

## 🚧 開発ガイドライン

### コード規約

- PEP 8スタイルガイドに従う
- 型ヒントを使用してコードの可読性を向上
- 非同期関数を適切に使用
- 例外処理を丁寧に行う

### 貢献方法

1. このリポジトリをフォークする
2. 新しいブランチを作成する (`git checkout -b feature/amazing-feature`)
3. 変更をコミットする (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュする (`git push origin feature/amazing-feature`)
5. プルリクエストを作成する

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

このプロジェクトは以下のオープンソースプロジェクトを利用しています：

- [FastAPI](https://fastapi.tiangolo.com/)
- [MarkItDown](https://github.com/microsoft/markitdown)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [HTTPX](https://www.python-httpx.org/)

---

Made with ❤️ by [PONOTECH](https://github.com/your-username)