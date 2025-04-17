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

BULAN_ORDER = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
    "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12
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

    login_data = get_sheet_data(SHEET_IDS['login'], 'Sheet1!A2:B100')

    for row in login_data:
        if len(row) >= 2:
            sheet_username = row[0].strip().lower()
            sheet_password = row[1].strip()
            if username == sheet_username and password == sheet_password:
                return jsonify({"status": "success"})

    return jsonify({"status": "failed"}), 401

@app.route("/search", methods=["GET"])
def search_data():
    try:
        city_from = request.args.get("city_from", "").lower()
        city_to = request.args.get("city_to", "").lower()
        revenue_flag = "revenue" in request.args
        performance_flag = "performance" in request.args

        if revenue_flag and city_from and city_to:
            return handle_revenue(city_from, city_to)
        elif performance_flag and city_to:
            return handle_performance(city_to)
        else:
            return jsonify({"error": "Parameter tidak lengkap atau salah."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_performance(city_to):
    try:
        print(f"Mencari data performance untuk: {city_to}")
        data = get_sheet_data(SHEET_IDS['performance'], "Sheet2!A:Z")

        if not data or len(data) < 2:
            return jsonify({"error": "Data performance tidak ditemukan."})

        hasil = defaultdict(list)
        for row in data[1:]:
            if len(row) < 6:
                continue
            tahun, bulan = row[0].strip(), row[1].strip()
            tujuan = row[2].lower()
            wilayah = row[3].strip()
            performance = row[4].strip()
            keterangan = row[5].strip()

            if city_to in tujuan:
                key = f"{bulan} {tahun}"
                hasil[key].append({
                    "wilayah": wilayah,
                    "performance": performance,
                    "keterangan": keterangan
                })

        if not hasil:
            return jsonify({"message": "Data tidak ditemukan."})

        sorted_keys = sorted(hasil.keys(), key=lambda x: (int(x.split()[1]), BULAN_ORDER.get(x.split()[0], 13)))

        return jsonify({
            "kota_tujuan": city_to.title(),
            "detail_performance": {key: hasil[key] for key in sorted_keys}
        })
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": "Terjadi kesalahan pada performance."}), 500

if __name__ == "__main__":
    app.run(debug=True)
