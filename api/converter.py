from markitdown import MarkItDown
from typing import Dict, Tuple, Optional, List
from tempfile import NamedTemporaryFile
import os
import asyncio
from datetime import datetime
import mimetypes
from pathlib import Path
from bs4 import BeautifulSoup

from models import ConversionResult, ConversionMetadata
from crawler import WebCrawler
import tasks

class MarkdownConverter:
    """ウェブサイトをMarkdownに変換するクラス"""
    
    def __init__(self):
        """コンバーターの初期化"""
        self.markitdown = MarkItDown()
    
    async def convert_website(
        self, 
        url: str, 
        crawl_depth: int = 1, 
        include_images: bool = True,
        task_id: Optional[str] = None
    ) -> ConversionResult:
        """
        ウェブサイトをクロールしてMarkdownに変換する
        
        Args:
            url: クロール対象のURL
            crawl_depth: クロールする深度
            include_images: 画像を含めるかどうか
            task_id: 進捗報告用のタスクID(省略可)
            
        Returns:
            ConversionResult: 変換結果
        """
        # 進捗状況の更新
        if task_id:
            tasks.update_task_progress(
                task_id, 
                10, 
                "ウェブサイトのクローリングを開始します"
            )
        
        # ウェブサイトのクローリング
        crawler = WebCrawler(url, max_depth=crawl_depth, include_images=include_images)
        pages, images = await crawler.crawl(task_id)
        
        # 進捗状況の更新
        if task_id:
            tasks.update_task_progress(
                task_id, 
                75, 
                "クローリングが完了しました。Markdownに変換します"
            )
        
        # ページをMarkdownに変換
        markdown_contents = await self._convert_pages_to_markdown(pages)
        
        # 進捗状況の更新
        if task_id:
            tasks.update_task_progress(
                task_id, 
                90, 
                "Markdown変換が完了しました"
            )
        
        # 全てのMarkdownを結合
        combined_markdown = self._combine_markdown(markdown_contents, url)
        
        # サイトのタイトルを取得
        title = crawler.get_title() or "変換されたウェブサイト"
        
        # メタデータの作成
        metadata = ConversionMetadata(
            source_url=url,
            title=title,
            page_count=len(pages),
            crawl_depth=crawl_depth,
            include_images=include_images,
            converted_at=datetime.now().isoformat()
        )
        
        # 結果の作成
        result = ConversionResult(
            task_id=task_id or "",
            markdown=combined_markdown,
            metadata=metadata
        )
        
        # 進捗状況の更新
        if task_id:
            tasks.update_task_progress(
                task_id, 
                95, 
                "結果を生成しました"
            )
        
        return result
    
    async def convert_file(
        self,
        file_path: str,
        original_filename: str,
        task_id: Optional[str] = None
    ) -> ConversionResult:
        """
        ファイルをMarkdownに変換する
        
        Args:
            file_path: 変換するファイルのパス
            original_filename: 元のファイル名
            task_id: 進捗報告用のタスクID(省略可)
            
        Returns:
            ConversionResult: 変換結果
        """
        try:
            # 進捗状況の更新
            if task_id:
                tasks.update_task_progress(
                    task_id, 
                    10, 
                    f"ファイル {original_filename} の変換を開始します"
                )
            
            # ファイルの拡張子を取得
            file_ext = os.path.splitext(original_filename)[1].lower()
            
            # 進捗状況の更新
            if task_id:
                tasks.update_task_progress(
                    task_id, 
                    30, 
                    "ファイルを解析中..."
                )
            
            # MarkItDownを使用してファイルをMarkdownに変換
            conversion_result = self.markitdown.convert(file_path)
            markdown_content = conversion_result.text_content
            
            # 進捗状況の更新
            if task_id:
                tasks.update_task_progress(
                    task_id, 
                    90, 
                    "Markdown変換が完了しました"
                )
            
            # ファイル名をタイトルとして使用
            title = os.path.basename(original_filename)
            
            # メタデータの作成
            metadata = ConversionMetadata(
                source_url=f"file://{original_filename}",  # ローカルファイルのためURL形式なし
                title=title,
                page_count=1,  # ファイルは単一ページとして扱う
                crawl_depth=0,  # ファイル変換なのでクロール深度は0
                include_images=True,  # 不使用だが設定
                converted_at=datetime.now().isoformat()
            )
            
            # 結果の作成
            result = ConversionResult(
                task_id=task_id or "",
                markdown=markdown_content,
                metadata=metadata
            )
            
            # 進捗状況の更新
            if task_id:
                tasks.update_task_progress(
                    task_id, 
                    95, 
                    "結果を生成しました"
                )
            
            # 一時ファイルを削除
            if os.path.exists(file_path):
                os.unlink(file_path)
            
            return result
            
        except Exception as e:
            # エラー発生時は一時ファイルを削除
            if os.path.exists(file_path):
                os.unlink(file_path)
            
            # エラーの再スロー
            raise Exception(f"ファイル変換中にエラーが発生しました: {str(e)}")
    
    async def _convert_pages_to_markdown(self, pages: Dict[str, str]) -> Dict[str, str]:
        """
        複数のHTMLページをMarkdownに変換する
        
        Args:
            pages: URL -> HTML内容の辞書
            
        Returns:
            Dict[str, str]: URL -> Markdown内容の辞書
        """
        results: Dict[str, str] = {}
        
        for url, html in pages.items():
            try:
                # 一時ファイルにHTMLを書き込む
                with NamedTemporaryFile(suffix=".html", delete=False) as temp:
                    temp_path = temp.name
                    temp.write(html.encode('utf-8'))
                
                # MarkItDownを使用してHTMLをMarkdownに変換
                conversion_result = self.markitdown.convert(temp_path)
                markdown_content = conversion_result.text_content
                
                # ヘッダーにURLを追加
                page_title = self._extract_title(html) or url
                markdown_with_url = f"# {page_title}\n\n*元のURL: {url}*\n\n{markdown_content}"
                
                results[url] = markdown_with_url
                
                # 一時ファイルを削除
                os.unlink(temp_path)
                
            except Exception as e:
                # エラーの場合はシンプルなエラーメッセージを返す
                results[url] = f"# {url}\n\n*変換中にエラーが発生しました: {str(e)}*\n"
        
        return results
    
    def _extract_title(self, html: str) -> Optional[str]:
        """
        HTMLからタイトルを抽出する
        
        Args:
            html: HTML内容
            
        Returns:
            Optional[str]: タイトルまたはNone
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.text.strip()
            h1_tag = soup.find('h1')
            if h1_tag:
                return h1_tag.text.strip()
        except:
            pass
        return None
    
    def _combine_markdown(self, markdown_contents: Dict[str, str], base_url: str) -> str:
        """
        複数のMarkdownコンテンツを結合する
        
        Args:
            markdown_contents: URL -> Markdown内容の辞書
            base_url: ベースURL
            
        Returns:
            str: 結合したMarkdown
        """
        # ベースURLのコンテンツを先頭に持ってくる
        ordered_urls = list(markdown_contents.keys())
        if base_url in ordered_urls:
            ordered_urls.remove(base_url)
            ordered_urls.insert(0, base_url)
        
        # 各ページのMarkdownを結合
        combined = []
        for url in ordered_urls:
            content = markdown_contents[url]
            combined.append(content)
            combined.append("\n---\n\n")  # ページ区切り
        
        # 末尾の区切りを削除
        if combined and combined[-1] == "\n---\n\n":
            combined.pop()
        
        return "".join(combined)