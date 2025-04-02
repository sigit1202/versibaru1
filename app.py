@app.route('/search', methods=['GET'])
def search_data():
    city_from = request.args.get('city_from', '').lower()
    city_to = request.args.get('city_to', '').lower()

    summary = {
        "deskripsi": f"{city_from.title()} - {city_to.title()}",
        "total_bulan": 0,
        "total_stt": 0.0,
        "total_berat": 0.0,
        "total_revenue": 0.0,
        "tahun": "",
        "bulan": [],
        "detail_bulan": {}
    }

    bulan_terdeteksi = set()

    for sheet_name, sheet_id in SHEET_IDS.items():
        range_name = 'Sheet2!A:Z'
        data = get_sheet_data(sheet_id, range_name)

        if not data or len(data) < 2:
            continue

        for row in data[1:]:
            if len(row) >= 9:
                bulan = row[1].strip()
                tahun = row[0].strip()
                city_from_data = row[4].lower()
                city_to_data = row[5].lower()

                if city_from in city_from_data and city_to in city_to_data:
                    try:
                        stt = float(row[6].replace(',', '').strip() or 0)
                        berat = float(row[7].replace(',', '').strip() or 0)
                        revenue = float(row[8].replace(',', '').strip() or 0)
                    except ValueError:
                        continue

                    if not summary["tahun"]:
                        summary["tahun"] = tahun

                    if bulan not in summary["detail_bulan"]:
                        summary["detail_bulan"][bulan] = {
                            "stt": 0.0,
                            "berat": 0.0,
                            "revenue": 0.0
                        }

                    summary["detail_bulan"][bulan]["stt"] += stt
                    summary["detail_bulan"][bulan]["berat"] += berat
                    summary["detail_bulan"][bulan]["revenue"] += revenue

                    summary["total_stt"] += stt
                    summary["total_berat"] += berat
                    summary["total_revenue"] += revenue

                    bulan_terdeteksi.add(bulan)

    summary["bulan"] = sorted(list(bulan_terdeteksi))
    summary["total_bulan"] = len(bulan_terdeteksi)

    # 🔢 Format jadi angka bulat ribuan (tanpa desimal)
    summary["total_stt"] = f"{summary['total_stt']:,.0f}"
    summary["total_berat"] = f"{summary['total_berat']:,.0f}"
    summary["total_revenue"] = f"{summary['total_revenue']:,.0f}"

    for bulan in summary["detail_bulan"]:
        detail = summary["detail_bulan"][bulan]
        detail["stt"] = f"{detail['stt']:,.0f}"
        detail["berat"] = f"{detail['berat']:,.0f}"
        detail["revenue"] = f"{detail['revenue']:,.0f}"

    return jsonify(summary)
