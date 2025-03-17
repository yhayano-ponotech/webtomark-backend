# MarkItDown - ウェブサイトクローラー＆変換アプリケーション（バックエンド）

![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MarkItDown](https://img.shields.io/badge/MarkItDown-0.1.0a1-orange)
![Beautiful Soup](https://img.shields.io/badge/BeautifulSoup-4-green)

## 📖 概要

MarkItDownバックエンドは、ウェブサイトをクローリング・スクレイピングし、Markdown形式に変換するAPIサーバーです。FastAPI（Python）で構築されており、非同期処理によるパフォーマンス最適化が行われています。

## ✨ 機能

- ウェブサイトURLのクローリングと構造抽出
- 指定した深度までの再帰的クローリング
- MarkItDownライブラリによるMarkdown変換処理
- 非同期タスク管理と進捗状況の追跡
- RESTful APIによるフロントエンドとの連携

## 🛠️ 技術スタック

- **FastAPI**: 高速なPythonウェブフレームワーク
- **Pydantic**: データバリデーション
- **MarkItDown**: Markdown変換ライブラリ
- **Beautiful Soup / lxml**: スクレイピングライブラリ
- **HTTPX**: 非同期HTTPクライアント
- **Uvicorn**: ASGIサーバー

## 🚀 セットアップ方法

### 前提条件

- Python 3.10以上
- pip（Pythonパッケージマネージャー）

### インストール

1. リポジトリをクローンする:

```bash
git clone https://github.com/your-username/markitdown-backend.git
cd markitdown-backend
```

2. 仮想環境を作成して有効化する:

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

3. 依存関係をインストールする:

```bash
pip install -r api/requirements.txt
```

4. 環境変数の設定（オプション）:

`.env` ファイルを作成して環境変数を設定します:

```
MAX_CRAWL_DEPTH=5
```

### 開発サーバーの起動

開発サーバーを起動するには以下のコマンドを実行します:

```bash
cd api
python run_server.py
```

サーバーは `http://localhost:8000` で実行されます。Swagger APIドキュメントは `http://localhost:8000/docs` で確認できます。

## 📑 APIエンドポイント

| エンドポイント | メソッド | 説明 |
|---------------|--------|------|
| `/` | GET | APIの基本情報 |
| `/api/convert/` | POST | ウェブサイト変換リクエストの開始 |
| `/api/tasks/{task_id}/` | GET | タスク状態の確認 |
| `/api/tasks/{task_id}/result/` | GET | 変換結果の取得 |

### リクエスト例

#### 変換リクエスト

```json
POST /api/convert/
{
  "url": "https://example.com",
  "options": {
    "crawl_depth": 2,
    "include_images": true
  }
}
```

#### レスポンス

```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### タスク状態の確認

```
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000/
```

#### レスポンス

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "ページをクロール中: https://example.com (深度 1/2)"
}
```

#### 結果の取得

```
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000/result/
```

## 🧩 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `MAX_CRAWL_DEPTH` | 最大クロール深度の制限 | `5` |

## 📁 プロジェクト構造

```
/
├── api/                   # APIアプリケーションフォルダ
│   ├── __init__.py        # パッケージ初期化
│   ├── main.py            # FastAPIアプリケーションのメインファイル
│   ├── converter.py       # Markdown変換ロジック
│   ├── crawler.py         # ウェブクローリングロジック
│   ├── models.py          # Pydanticモデル定義
│   ├── tasks.py           # 非同期タスク管理
│   ├── requirements.txt   # 依存関係
│   └── run_server.py      # 開発サーバー起動スクリプト
└── .env                   # 環境変数（gitignoreに含める）
```

## 📊 パフォーマンスと制限

- Vercelのサーバーレス関数では実行時間が30秒に制限されるため、大規模サイトの完全クローリングは避けてください
- メモリ使用量にも制限（1GB）があります
- クロール深度は最大5に制限されています
- 同一ドメイン内のページのみクロールします

## 🔄 フロントエンドとの連携

このバックエンドAPIは対応するフロントエンドアプリケーションと連携します。フロントエンドのセットアップについては、フロントエンドリポジトリのREADMEを参照してください。

## 🌐 Vercelへのデプロイ

Vercelにデプロイするには、以下の手順に従ってください：

1. `vercel.json` ファイルをプロジェクトルートに作成:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

2. [Vercel CLI](https://vercel.com/download) をインストール:

```bash
npm i -g vercel
```

3. デプロイを実行:

```bash
vercel
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

このプロジェクトは以下のオープンソースプロジェクトを利用しています：

- [FastAPI](https://fastapi.tiangolo.com/)
- [MarkItDown](https://github.com/microsoft/markitdown)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [HTTPX](https://www.python-httpx.org/)

---

Made with ❤️ by [PONOTECH](https://github.com/your-username)