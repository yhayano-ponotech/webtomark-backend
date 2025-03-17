from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Optional, List
import os

from models import ConversionRequest, TaskStatus, ConversionResult
from converter import MarkdownConverter
import tasks

# 環境変数から設定を読み込み
MAX_CRAWL_DEPTH = int(os.getenv("MAX_CRAWL_DEPTH", "5"))

# CORS用のオリジン設定を環境変数から取得
# カンマ区切りの文字列から配列に変換（例: "http://localhost:3000,https://example.com"）
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
# ["*"]のままの場合は、すべてのオリジンを許可
if len(ALLOWED_ORIGINS) == 1 and ALLOWED_ORIGINS[0] == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    # 各URLの前後の空白を削除
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

# FastAPIアプリケーションの作成
app = FastAPI(
    title="MarkItDown API",
    description="ウェブサイトをクローリングしてMarkdownに変換するAPI",
    version="0.1.0"
)

# CORSミドルウェアの設定（環境変数から許可オリジンを設定）
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Markdownコンバーターのインスタンス作成
converter = MarkdownConverter()

# 依存関係：クロール深度の検証
def validate_crawl_depth(request: ConversionRequest):
    if request.options.crawl_depth > MAX_CRAWL_DEPTH:
        request.options.crawl_depth = MAX_CRAWL_DEPTH
    return request

# ルートエンドポイント（APIの説明）
@app.get("/")
def read_root():
    return {
        "message": "MarkItDown ウェブサイトクローラー＆変換API",
        "version": "0.1.0",
        "endpoints": {
            "/api/convert/": "ウェブサイトをMarkdownに変換するリクエストを開始",
            "/api/tasks/{task_id}/": "タスクのステータスを確認",
            "/api/tasks/{task_id}/result/": "変換結果を取得",
        }
    }

# 変換リクエストを開始するエンドポイント
@app.post("/api/convert/", response_model=dict)
async def start_conversion(
    request: ConversionRequest = Depends(validate_crawl_depth),
    background_tasks: BackgroundTasks = None,
):
    # タスクIDの生成（リクエストから渡されない場合）
    task_id = request.task_id or str(uuid.uuid4())
    request.task_id = task_id
    
    # バックグラウンドタスクの開始
    await tasks.start_background_task(
        task_id,
        converter.convert_website,
        request.url,
        request.options.crawl_depth,
        request.options.include_images
    )
    
    return {"taskId": task_id}

# タスクのステータスを確認するエンドポイント
@app.get("/api/tasks/{task_id}/", response_model=TaskStatus)
async def get_task_status(task_id: str):
    task_status = tasks.get_task_status(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="指定されたタスクが見つかりません")
    return task_status

# 変換結果を取得するエンドポイント
@app.get("/api/tasks/{task_id}/result/", response_model=ConversionResult)
async def get_task_result(task_id: str):
    # タスクの状態を確認
    task_status = tasks.get_task_status(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="指定されたタスクが見つかりません")
    
    # タスクが完了していない場合はエラー
    if task_status.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"タスクはまだ完了していません (現在の状態: {task_status.status})"
        )
    
    # 結果を取得
    result = tasks.get_task_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="指定されたタスクの結果が見つかりません")
    
    return result

# サーバーレス環境（Vercel）での起動ポイント
# VercelのPython runtime向けにこの形式が必要
handler = app