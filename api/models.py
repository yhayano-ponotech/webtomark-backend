from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import re

class ConversionOptions(BaseModel):
    """変換オプション用のモデル"""
    crawl_depth: int = Field(1, ge=1, le=5, description="クロールする深さ（1〜5）")
    include_images: bool = Field(True, description="画像を含めるかどうか")

class ConversionRequest(BaseModel):
    """変換リクエスト用のモデル"""
    url: str = Field(..., description="クロール対象のURL")
    options: ConversionOptions = Field(default_factory=ConversionOptions)
    task_id: Optional[str] = None
    
    @validator('url')
    def validate_url(cls, value):
        # URLの基本的な検証
        url_pattern = re.compile(
            r'^(https?://)?' # http:// または https://
            r'([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+' # ドメイン
            r'[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]' # TLD
            r'(/[-A-Za-z0-9+&@#/%?=~_|!:,.;]*)*' # パス
            r'(\?[-A-Za-z0-9+&@#/%=~_|!:,.;]*)?'  # クエリパラメータ
        )
        if not url_pattern.match(value):
            raise ValueError("無効なURL形式です")
        
        # URLスキームが省略されている場合、httpsを追加
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
            
        return value

class TaskStatus(BaseModel):
    """タスクステータス用のモデル"""
    task_id: str
    status: Literal['pending', 'processing', 'completed', 'failed']
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None

class ConversionMetadata(BaseModel):
    """変換結果のメタデータ用のモデル"""
    source_url: str
    title: Optional[str] = None
    page_count: Optional[int] = None
    crawl_depth: int
    include_images: bool
    converted_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    file_type: Optional[str] = None  # ファイル変換時のファイルタイプ

class ConversionResult(BaseModel):
    """変換結果用のモデル"""
    task_id: str
    markdown: str
    metadata: ConversionMetadata