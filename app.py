import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re

st.title("📋 Udipop Scraper Tender LPSE Indonesia")

# Fungsi bantu untuk konversi nilai HPS ke float
def parse_hps(hps_text):
    try:
        angka = re.sub(r'[^\d]', '', hps_text)
        return float(angka)
    except:
        return 0.0

# Fungsi untuk ambil tender dari satu domain
def ambil_tender(domain):
    url = f"{domain}/eproc4/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")[1:]  # Skip header
        hasil = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                hps_text = cols[3].text.strip()
                hps_value = parse_hps(hps_text)
                if hps_value >= 200_000_000:
                    hasil.append({
                        "LPSE": domain.replace("https://", ""),
                        "Nama Paket": cols[1].text.strip(),
                        "HPS": hps_text,
                        "Akhir Pendaftaran": cols[4].text.strip()
                    })
        return hasil
    except Exception as e:
        return [{
            "LPSE": domain.replace("https://", ""),
            "Nama Paket": f"Gagal ambil data: {e}",
            "HPS": "-",
            "Akhir Pendaftaran": "-"
        }]

# Baca daftar domain
with open("daftar_lpse.txt", "r") as f:
    list_domain = [line.strip() for line in f.readlines() if line.strip()]

st.write(f"📡 Mengambil tender aktif dari {len(list_domain)} domain LPSE...")

# Proses paralel agar cepat
all_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(ambil_tender, list_domain)
    for result in results:
        all_data.extend(result)

# Tampilkan data jika ada
if all_data:
    df = pd.DataFrame(all_data)
    st.success(f"Ditemukan {len(df)} data tender aktif dengan HPS > 200 juta!")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "tender_lpse.csv", "text/csv")
else:
    st.warning("Tidak ada data tender yang ditemukan.")
