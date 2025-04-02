from flask import Flask, jsonify, request
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os

app = Flask(__name__)

# Authentication Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'  # Pastikan file json Service Account berada di lokasi ini

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize Sheets API
service = build('sheets', 'v4', credentials=credentials)

# Google Sheets ID dan range untuk sheet2
SHEET_IDS = {
    'sheet1': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'sheet2': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
}

# Fungsi untuk mengambil data dari Google Sheets
def get_sheet_data(sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

@app.route('/search', methods=['GET'])
def search_data():
    # Mendapatkan parameter pencarian dari request
    city_from = request.args.get('city_from')
    city_to = request.args.get('city_to')
    month = request.args.get('month')

    result = {}

    # Mengambil data dari kedua Google Sheets
    for sheet_name, sheet_id in SHEET_IDS.items():
        # Menetapkan range untuk mengambil data dari sheet2
        range_name = f'Sheet2!A:Z'  # Mengambil semua kolom dari Sheet2
        data = get_sheet_data(sheet_id, range_name)

        # Mencari data yang cocok berdasarkan parameter pencarian
        for row in data:
            # Pastikan bahwa kolom yang diambil sesuai dengan kebutuhan (misalnya kolom kota dan bulan)
            if len(row) >= 3:  # Misalkan data ada di kolom 1, 2, 3 untuk kota asal, kota tujuan, dan bulan
                city_from_data = row[4]  # Asumsi: kolom pertama adalah kota asal
                city_to_data = row[5]    # Asumsi: kolom kedua adalah kota tujuan
                month_data = row[1]      # Asumsi: kolom ketiga adalah bulan

                # Cek apakah data cocok dengan query pencarian
                if city_from in city_from_data and city_to in city_to_data and month in month_data:
                    if sheet_name not in result:
                        result[sheet_name] = []
                    result[sheet_name].append(row)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
