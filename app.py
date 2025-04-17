import os
import json
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

app = Flask(__name__)

# Load credential dari ENV
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
credentials_info = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
service = build('sheets', 'v4', credentials=credentials)

# ID dari tiga Google Sheets
SHEET_IDS = {
    'revenue': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'performance': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
    'login': '1n8gJ0DyvBR21eeDhnN6nECJZJYVtsIA-vVaq_ZPeHJA',
}

def get_sheet_data(sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    login_data = get_sheet_data(SHEET_IDS['login'], 'Sheet1!A2:B100')  # baca dari Sheet Login

    for row in login_data:
        if len(row) >= 2:
            sheet_username = row[0].strip().lower()
            sheet_password = row[1].strip()
            if username == sheet_username and password == sheet_password:
                return jsonify({"status": "success"})

    return jsonify({"status": "failed"}), 401

@app.route("/search", methods=["GET"])
def search_data():
    # ... kode pencarian ...

