import functions_framework
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from googleapiclient.discovery import build
from google.auth import default

# 【重要】作成したスプレッドシートのIDに書き換えてください
SPREADSHEET_ID = "your/spreadsheet_id"
# 書き込み先のシート名（デフォルトは シート1）
RANGE_NAME = "シート1!A1"

def append_to_sheet(rows):
    """スプレッドシートの末尾にデータを追記する"""
    creds, _ = default()
    service = build("sheets", "v4", credentials=creds)
    body = {
        'values': rows
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

@functions_framework.http
def scraping_to_drive(request):
    print("--- Scraping to Sheets Started ---")
    target_url = "https://quotes.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # データの抽出
        quote_elements = soup.find_all('div', class_='quote')
        rows = []
        # 初回書き込み時のみヘッダーを入れたい場合は調整が必要ですが、
        # 今回はシンプルにデータのみをリスト化します
        for element in quote_elements:
            text = element.find('span', class_='text').get_text()
            author = element.find('small', class_='author').get_text()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 1行分のデータをリストとして追加
            rows.append([timestamp, text, author])
        # スプレッドシートへ追記
        if rows:
            append_to_sheet(rows)
            print(f"Successfully appended {len(rows)} rows.")
            return f"Success: {len(rows)} rows added to Google Sheets."
        else:
            return "No data found to scrape."
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Failed: {str(e)}", 500