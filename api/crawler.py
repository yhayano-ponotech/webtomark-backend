import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Tuple, Optional
import asyncio
import tasks

class WebCrawler:
    """ウェブサイトクローリングクラス"""
    
    def __init__(self, base_url: str, max_depth: int = 1, include_images: bool = True):
        """
        クローラーの初期化
        
        Args:
            base_url: クロール開始URL
            max_depth: クロールする最大深度
            include_images: 画像を含めるかどうか
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.include_images = include_images
        self.visited_urls: Set[str] = set()
        self.pages: Dict[str, str] = {}  # URL -> HTML
        self.images: Dict[str, bytes] = {}  # URL -> 画像データ
        self.domain = urlparse(base_url).netloc
        
    async def crawl(self, task_id: Optional[str] = None) -> Tuple[Dict[str, str], Dict[str, bytes]]:
        """
        ウェブサイトをクロールする
        
        Args:
            task_id: 進捗報告用のタスクID(省略可)
            
        Returns:
            Tuple[Dict[str, str], Dict[str, bytes]]: 収集したページと画像
        """
        # 開始URLから再帰的にクロール
        await self._crawl_page(self.base_url, 0, task_id)
        
        # 進捗を95%に更新
        if task_id:
            tasks.update_task_progress(task_id, 95, "クローリングが完了しました")
        
        return self.pages, self.images
    
    async def _crawl_page(self, url: str, depth: int, task_id: Optional[str] = None) -> None:
        """
        再帰的にページをクロールする
        
        Args:
            url: クロールするURL
            depth: 現在の深度
            task_id: 進捗報告用のタスクID(省略可)
        """
        # 深度制限を超えた場合や既に訪問済みの場合はスキップ
        if depth > self.max_depth or url in self.visited_urls:
            return
        
        # 同じドメイン内のURLのみクロール
        if not self._is_same_domain(url):
            return
        
        # URLを訪問済みに追加
        self.visited_urls.add(url)
        
        # 進捗状況の更新 (初期20%から段階的に70%まで)
        if task_id:
            progress = min(20 + int(50 * (depth + 1) / (self.max_depth + 1)), 70)
            tasks.update_task_progress(
                task_id, 
                progress, 
                f"ページをクロール中: {url} (深度 {depth}/{self.max_depth})"
            )
        
        try:
            # ページの取得
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    return
                
                # HTMLコンテンツを保存
                html_content = response.text
                self.pages[url] = html_content
                
                # 深度が最大に達した場合はリンクの抽出をスキップ
                if depth == self.max_depth:
                    return
                
                # BeautifulSoupでHTMLを解析
                soup = BeautifulSoup(html_content, 'lxml')
                
                # リンクを抽出して次の深度でクロール
                links = soup.find_all('a', href=True)
                next_urls = []
                
                for link in links:
                    next_url = urljoin(url, link['href'])
                    if next_url not in self.visited_urls and self._is_same_domain(next_url):
                        next_urls.append(next_url)
                
                # 画像を抽出
                if self.include_images:
                    await self._extract_images(soup, url, client)
                
                # 次のURLを並行してクロール (最大5つまで同時に)
                tasks_list = []
                for i in range(0, len(next_urls), 5):
                    batch = next_urls[i:i+5]
                    tasks_list.append(asyncio.gather(
                        *[self._crawl_page(next_url, depth + 1, task_id) for next_url in batch]
                    ))
                
                for task_batch in tasks_list:
                    await task_batch
                    
        except (httpx.RequestError, httpx.HTTPStatusError, Exception) as e:
            # エラーをログ出力など（実際の実装ではロギングを追加）
            print(f"Error crawling {url}: {str(e)}")
    
    async def _extract_images(self, soup: BeautifulSoup, page_url: str, client: httpx.AsyncClient) -> None:
        """
        ページから画像を抽出する
        
        Args:
            soup: BeautifulSoupオブジェクト
            page_url: 現在のページURL
            client: HTTPクライアント
        """
        if not self.include_images:
            return
        
        images = soup.find_all('img', src=True)
        for img in images:
            try:
                img_url = urljoin(page_url, img['src'])
                
                # 既に取得済みの場合はスキップ
                if img_url in self.images:
                    continue
                
                # 同じドメイン内の画像のみ取得
                if not self._is_same_domain(img_url):
                    continue
                
                # 画像を取得
                img_response = await client.get(img_url)
                if img_response.status_code == 200:
                    self.images[img_url] = img_response.content
            except Exception as e:
                # エラーをログ出力など
                print(f"Error extracting image {img.get('src', '')}: {str(e)}")
    
    def _is_same_domain(self, url: str) -> bool:
        """
        URLが同じドメイン内かどうかを確認する
        
        Args:
            url: 確認するURL
            
        Returns:
            bool: 同じドメインの場合はTrue
        """
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.domain or parsed_url.netloc == ''
    
    def get_title(self) -> Optional[str]:
        """
        クロールしたサイトのタイトルを取得する
        
        Returns:
            Optional[str]: サイトのタイトル
        """
        if not self.pages:
            return None
        
        # 基本URLのタイトルを取得
        if self.base_url in self.pages:
            soup = BeautifulSoup(self.pages[self.base_url], 'lxml')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.text.strip()
        
        # 基本URLがない場合は最初のページのタイトルを使用
        first_page = next(iter(self.pages.values()))
        soup = BeautifulSoup(first_page, 'lxml')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.text.strip()
            
        return None