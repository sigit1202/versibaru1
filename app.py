import os
import json
from flask import Flask, jsonify, request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Inisialisasi Flask app
app = Flask(__name__)

# Ambil credentials dari environment
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
credentials_info = json.loads(credentials_json)

credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

service = build('sheets', 'v4', credentials=credentials)

# Data ID Google Sheets
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
    city_from = request.args.get('city_from', '').lower()
    city_to = request.args.get('city_to', '').lower()

    summary = {
        "deskripsi": f"{city_from.title()} - {city_to.title()}",
        "total_bulan": 0,
        "total_stt": 0,
        "total_berat": 0,
        "total_revenue": 0,
        "tahun": "2025",
        "bulan": [],
        "detail_bulan": {}
    }

    for sheet_id in SHEET_IDS.values():
        data = get_sheet_data(sheet_id, 'Sheet2!A:Z')
        if not data or len(data) < 2:
            continue

        for row in data[1:]:
            if len(row) < 7:
                continue

            bulan, stt_raw, berat_raw, revenue_raw = row[1], row[2], row[3], row[6]
            from_data = row[4].lower()
            to_data = row[5].lower()

            if city_from in from_data and city_to in to_data:
                try:
                    stt = int(stt_raw.replace(",", "").strip())
                    berat = int(berat_raw.replace(",", "").strip())
                    revenue = int(revenue_raw.replace(",", "").strip())
                except ValueError:
                    continue  # Skip baris jika data tidak valid

                if bulan not in summary["detail_bulan"]:
                    summary["detail_bulan"][bulan] = {
                        "stt": 0,
                        "berat": 0,
                        "revenue": 0
                    }
                    summary["bulan"].append(bulan)

                summary["detail_bulan"][bulan]["stt"] += stt
                summary["detail_bulan"][bulan]["berat"] += berat
                summary["detail_bulan"][bulan]["revenue"] += revenue

                summary["total_stt"] += stt
                summary["total_berat"] += berat
                summary["total_revenue"] += revenue

    summary["total_bulan"] = len(summary["bulan"])

    # Format angka dengan titik sebagai pemisah ribuan
    def fmt(num): return f"{num:,}".replace(",", ".")

    for bulan in summary["detail_bulan"]:
        for k in summary["detail_bulan"][bulan]:
            summary["detail_bulan"][bulan][k] = fmt(summary["detail_bulan"][bulan][k])

    summary["total_stt"] = fmt(summary["total_stt"])
    summary["total_berat"] = fmt(summary["total_berat"])
    summary["total_revenue"] = fmt(summary["total_revenue"])

    return jsonify(summary)


if __name__ == '__main__':
    app.run(debug=True)
