import os
import json
from flask import Flask, jsonify, request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

credentials_json = os.getenv("GOOGLE_CREDENTIALS")
credentials_info = json.loads(credentials_json)

credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

service = build('sheets', 'v4', credentials=credentials)

SHEET_IDS = {
    'sheet1': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'sheet2': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
}

def get_sheet_data(sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

@app.route('/search', methods=['GET'])
def search_data():
    city_from = request.args.get('city_from').lower()
    city_to = request.args.get('city_to').lower()
    month = request.args.get('month').lower()

    result = {}

    for sheet_name, sheet_id in SHEET_IDS.items():
        range_name = 'Sheet2!A:Z'
        data = get_sheet_data(sheet_id, range_name)

        for row in data:
            if len(row) >= 6:
                city_from_data = row[4].lower().strip()
                city_to_data = row[5].lower().strip()
                month_data = row[1].lower().strip()

                if city_from in city_from_data and city_to in city_to_data and month in month_data:
                    result.setdefault(sheet_name, []).append(row)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
