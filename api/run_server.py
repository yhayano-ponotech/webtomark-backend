"""
FastAPIサーバーを直接起動するスクリプト
このスクリプトを使用すると、直接Pythonインタプリタから
uvicornを起動するため、モジュールの検索パスの問題を回避できます。

ローカル開発専用スクリプト - 本番環境(Render.com)では使用しません。
"""
import os
import uvicorn

if __name__ == "__main__":
    print("MarkItDown API サーバーを起動中...")
    
    # 環境変数からポート番号を取得（デフォルトは8000）
    port = int(os.getenv("PORT", "8000"))
    
    # ホストをlocalhostに設定（ローカル開発用）
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
    
    print(f"サーバーが http://127.0.0.1:{port} で起動しました")
    print(f"APIドキュメントは http://127.0.0.1:{port}/docs で確認できます")