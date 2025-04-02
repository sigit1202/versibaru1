import os
import json
from flask import Flask, jsonify, request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

app = Flask(__name__)

# Ambil credentials dari environment
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
credentials_info = json.loads(credentials_json)

credentials = Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

service = build('sheets', 'v4', credentials=credentials)

SHEET_IDS = {
    'sheet1': '1cpzDf5mI1bm6U5JlfMvxolltI4Abrch2Ed4JQF4RoiA',
    'sheet2': '1dqYlI9l6gKomfApHyWiWTTZK8Fb7K_yM7JHuw6dT6bM',
}

# Urutan bulan
BULAN_ORDER = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
    "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12
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
        "tahun": "",  # ← diisi nanti
        "bulan": [],
        "detail_bulan": {}
    }

    bulan_dict = defaultdict(lambda: {"stt": 0, "berat": 0, "revenue": 0})

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
                key = f"{tahun}-{bulan}"
                bulan_dict[key]["stt"] += stt
                bulan_dict[key]["berat"] += berat
                bulan_dict[key]["revenue"] += revenue
                summary["total_stt"] += stt
                summary["total_berat"] += berat
                summary["total_revenue"] += revenue

    # Urutkan berdasarkan tahun dan bulan
    sorted_keys = sorted(
        bulan_dict.keys(),
        key=lambda x: (int(x.split('-')[0]), BULAN_ORDER.get(x.split('-')[1], 13))
    )

    tahun_set = set()

    for key in sorted_keys:
        tahun, bulan = key.split('-')
        tahun_set.add(tahun)
        detail = bulan_dict[key]

        summary["bulan"].append(bulan)
        summary["detail_bulan"][bulan] = {
            "stt": f"{detail['stt']:,}".replace(",", "."),
            "berat": f"{detail['berat']:,}".replace(",", "."),
            "revenue": f"{detail['revenue']:,}".replace(",", ".")
        }

    summary["total_bulan"] = len(summary["bulan"])
    summary["total_stt"] = f"{summary['total_stt']:,}".replace(",", ".")
    summary["total_berat"] = f"{summary['total_berat']:,}".replace(",", ".")
    summary["total_revenue"] = f"{summary['total_revenue']:,}".replace(",", ".")
    summary["tahun"] = ", ".join(sorted(tahun_set))

    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
