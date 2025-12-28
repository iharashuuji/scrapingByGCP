import functions_framework
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth import default
from datetime import datetime
import os
import suminoe
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("FOLDER_ID")
def upload_csv_to_drive(file_path, filename):
    creds, _ = default()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(
        file_path,
        mimetype="text/csv"
    )

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

@functions_framework.http
def hello_http(request):
    print("start")
    result = suminoe.run()

    # DataFrame → CSV
    df = pd.DataFrame(result)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scrape_{timestamp}.csv"
    file_path = f"/tmp/{filename}"

    df.to_csv(file_path, index=False, encoding="utf-8-sig")

    upload_csv_to_drive(file_path, filename)

    print(f"CSV saved: {filename}")
    return "CSV uploaded to Google Drive"