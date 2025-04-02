import os
import json
from flask import Flask, jsonify, request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# Ambil credentials dari environment variable
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
if not credentials_json:
    raise ValueError("Environment variable GOOGLE_CREDENTIALS is missing")

credentials_info = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# Inisialisasi Google Sheets API
service = build('sheets', 'v4', credentials=credentials)

# ID Google Sheets
SHEET_IDS = {
    'sheet1': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'sheet2': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
}

# Fungsi ambil data dari Google Sheets
def get_sheet_data(sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

# Endpoint pencarian
@app.route('/search', methods=['GET'])
def search_data():
    city_from = request.args.get('city_from', '').lower()
    city_to = request.args.get('city_to', '').lower()
    month = request.args.get('month', '').lower()

    result = {}

    for sheet_name, sheet_id in SHEET_IDS.items():
        range_name = 'Sheet2!A:Z'
        data = get_sheet_data(sheet_id, range_name)

        for row in data[1:]:  # skip header
            if len(row) >= 6:
                row_month = row[1].lower()
                row_city_from = row[4].lower()
                row_city_to = row[5].lower()

                print("Checking row:", row)
                print("Compare with:", city_from, city_to, month)

                if city_from in row_city_from and city_to in row_city_to and month in row_month:
                    if sheet_name not in result:
                        result[sheet_name] = []
                    result[sheet_name].append(row)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
