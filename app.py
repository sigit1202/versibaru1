import os
import json
from flask import Flask, jsonify, request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

app = Flask(__name__)

# Load credentials dari ENV
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
credentials_info = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
service = build('sheets', 'v4', credentials=credentials)

# Google Sheets
SHEET_IDS = {
    'sheet1': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'sheet2': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
}

# Urutan bulan
BULAN_ORDER = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
    "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

# Fungsi mengambil data dari sheet
def get_sheet_data(sheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

# Fungsi format angka
def format_angka(n):
    return f"{n:,}".replace(",", ".")

@app.route('/search', methods=['GET'])
def search_data():
    city_from = request.args.get('city_from', '').lower()
    city_to = request.args.get('city_to', '').lower()

    summary = {
        "deskripsi": f"{city_from.title()} - {city_to.title()}",
        "total_bulan": 0,
        "total_stt": 0,
        "total_berat": 0,
        "total_revenue": 0,
        "bulan": [],
        "detail_bulan": {},
        "total_per_tahun": {}  # ➕ penambahan grup total per tahun
    }

    bulan_dict = defaultdict(lambda: {"stt": 0, "berat": 0, "revenue": 0})
    tahun_dict = defaultdict(lambda: {"stt": 0, "berat": 0, "revenue": 0})

    for sheet_id in SHEET_IDS.values():
        data = get_sheet_data(sheet_id, 'Sheet2!A:Z')
        if not data or len(data) < 2:
            continue

        for row in data[1:]:
            if len(row) < 9:
                continue

            tahun = row[0].strip()
            bulan = row[1].strip()
            from_data = row[4].lower()
            to_data = row[5].lower()

            try:
                stt = int(row[6].replace(",", "").strip())
                berat = int(row[7].replace(",", "").strip())
                revenue = int(row[8].replace(",", "").strip())
            except Exception:
                continue

            if city_from in from_data and city_to in to_data:
                key = f"{bulan} {tahun}"  # e.g., "Desember 2024"
                bulan_dict[key]["stt"] += stt
                bulan_dict[key]["berat"] += berat
                bulan_dict[key]["revenue"] += revenue

                tahun_dict[tahun]["stt"] += stt
                tahun_dict[tahun]["berat"] += berat
                tahun_dict[tahun]["revenue"] += revenue

                summary["total_stt"] += stt
                summary["total_berat"] += berat
                summary["total_revenue"] += revenue

    # Sorting bulan berdasarkan tahun dan bulan
    sorted_keys = sorted(
        bulan_dict.keys(),
        key=lambda x: (int(x.split()[1]), BULAN_ORDER.get(x.split()[0], 13))
    )

    for key in sorted_keys:
        summary["bulan"].append(key)
        detail = bulan_dict[key]
        summary["detail_bulan"][key] = {
            "stt": format_angka(detail["stt"]),
            "berat": format_angka(detail["berat"]),
            "revenue": format_angka(detail["revenue"])
        }

    # Total per tahun
    for tahun in sorted(tahun_dict.keys()):
        summary["total_per_tahun"][tahun] = {
            "stt": format_angka(tahun_dict[tahun]["stt"]),
            "berat": format_angka(tahun_dict[tahun]["berat"]),
            "revenue": format_angka(tahun_dict[tahun]["revenue"]),
        }

    summary["total_bulan"] = len(summary["bulan"])
    summary["total_stt"] = format_angka(summary["total_stt"])
    summary["total_berat"] = format_angka(summary["total_berat"])
    summary["total_revenue"] = format_angka(summary["total_revenue"])

    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
