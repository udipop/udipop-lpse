# requirements.txt
# -----------------
# streamlit
# beautifulsoup4
# lxml
# requests
# pandas

# scraper_streamlit.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_hps(hps_str):
    try:
        hps_clean = hps_str.replace("Rp", "").replace(".", "").replace(",", ".").strip()
        return float(hps_clean)
    except:
        return 0

def scrape_lpse(url):
    try:
        res = requests.get(f"{url}/eproc4", timeout=10)
        res.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(res.text, "lxml")
    rows = soup.select("table.table.table-sm tbody tr")

    data = []
    current_category = None
    for row in rows:
        cols = row.find_all("td")

        # Baris kategori (colspan=4)
        if len(cols) == 1 or (len(cols) == 4 and not cols[1].find("a")):
            current_category = BeautifulSoup(str(row), "lxml").get_text(strip=True)
            continue

        # Baris data tender (4 kolom)
        if len(cols) == 4:
            nama_paket_tag = cols[1].find("a")
            nama_paket = nama_paket_tag.get_text(strip=True) if nama_paket_tag else cols[1].get_text(strip=True)
            hps_str = cols[2].get_text(strip=True)
            akhir_pendaftaran = cols[3].get_text(strip=True)
            hps_value = parse_hps(hps_str)

            if hps_value >= 200_000_000:
                link = url + nama_paket_tag['href'] if nama_paket_tag else ""
                data.append({
                    "Kategori": current_category,
                    "LPSE": url,
                    "Nama Paket": nama_paket,
                    "HPS": hps_value,
                    "Akhir Pendaftaran": akhir_pendaftaran,
                    "Link": link
                })
    return data

def scrape_all_lpse(file_path="daftar_lpse.txt"):
    try:
        with open(file_path) as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

    all_data = []
    for url in urls:
        all_data.extend(scrape_lpse(url))
    return all_data

# Streamlit App
st.title("Daftar Tender LPSE (HPS >= 200 Juta)")

with st.spinner("Mengambil data dari LPSE..."):
    data = scrape_all_lpse()

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Tidak ada data ditemukan atau terjadi kesalahan saat mengambil data.")
