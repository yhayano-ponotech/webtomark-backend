"""
FastAPIサーバーを直接起動するスクリプト
このスクリプトを使用すると、直接Pythonインタプリタから
uvicornを起動するため、モジュールの検索パスの問題を回避できます。
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("MarkItDown API サーバーを起動中...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)