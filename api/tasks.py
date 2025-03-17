from typing import Dict, Optional, Callable, Any
import asyncio
import time
from models import TaskStatus, ConversionResult

# インメモリタスク状態管理
# Vercelの関数実行時間制限(30秒)を考慮した簡易実装
# 実運用では永続化ストレージ(例：Vercel KV)を検討すべき
tasks: Dict[str, TaskStatus] = {}
results: Dict[str, ConversionResult] = {}

async def run_task(
    task_id: str, 
    func: Callable, 
    *args: Any, 
    **kwargs: Any
) -> None:
    """
    バックグラウンドでタスクを実行する関数
    
    Args:
        task_id: タスクID
        func: 実行する関数
        *args, **kwargs: 関数に渡す引数
    """
    try:
        # タスク状態を処理中に更新
        tasks[task_id] = TaskStatus(
            task_id=task_id,
            status="processing",
            progress=10,
            message="タスクを開始しました"
        )
        
        # 関数実行
        result = await func(*args, **kwargs, task_id=task_id)
        
        # 結果を保存
        results[task_id] = result
        
        # タスク状態を完了に更新
        tasks[task_id] = TaskStatus(
            task_id=task_id,
            status="completed",
            progress=100,
            message="タスクが完了しました"
        )
        
    except Exception as e:
        # エラー時の状態更新
        tasks[task_id] = TaskStatus(
            task_id=task_id,
            status="failed",
            progress=0,
            message=f"エラーが発生しました: {str(e)}"
        )

def create_task(task_id: str) -> None:
    """
    新しいタスクを作成する
    
    Args:
        task_id: タスクID
    """
    tasks[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        progress=0,
        message="タスクを作成しました"
    )

def get_task_status(task_id: str) -> Optional[TaskStatus]:
    """
    タスクの状態を取得する
    
    Args:
        task_id: タスクID
    
    Returns:
        TaskStatus or None: タスクの状態または存在しない場合はNone
    """
    return tasks.get(task_id)

def get_task_result(task_id: str) -> Optional[ConversionResult]:
    """
    タスクの結果を取得する
    
    Args:
        task_id: タスクID
    
    Returns:
        ConversionResult or None: タスクの結果または存在しない場合はNone
    """
    return results.get(task_id)

def update_task_progress(task_id: str, progress: int, message: Optional[str] = None) -> None:
    """
    タスクの進捗状況を更新する
    
    Args:
        task_id: タスクID
        progress: 進捗率(0-100)
        message: 進捗メッセージ(省略可)
    """
    if task_id in tasks:
        task = tasks[task_id]
        task.progress = progress
        if message:
            task.message = message

async def start_background_task(
    task_id: str, 
    func: Callable, 
    *args: Any, 
    **kwargs: Any
) -> None:
    """
    バックグラウンドでタスクを開始する
    
    Args:
        task_id: タスクID
        func: 実行する関数
        *args, **kwargs: 関数に渡す引数
    """
    # 新しいタスクを作成
    create_task(task_id)
    
    # バックグラウンドでタスクを実行
    asyncio.create_task(run_task(task_id, func, *args, **kwargs))

# 古いタスクを自動クリーンアップ (オプション)
def cleanup_old_tasks():
    """
    30分以上経過した古いタスクと結果を削除する
    実運用では別途実装が必要
    """
    # このサンプル実装では何もしない (Vercelサーバーレス環境では不要)
    pass