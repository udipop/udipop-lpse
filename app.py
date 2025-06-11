import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Scraper LPSE", layout="wide")
st.title("🔍 Scraper Tender LPSE SPSE 4.5")

# Baca daftar LPSE dari file
def read_lpse_list(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def parse_hps(hps_str):
    try:
        return int(hps_str.replace("Rp", "").replace(".00", "").replace(" ", "").replace(".", "").replace(",", ""))
    except:
        return 0

def scrape_lpse(url):
    base_url = url.rstrip("/")
    target_url = urljoin(base_url, "/eproc4")
    try:
        response = requests.get(target_url, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")
        data = []
        current_kategori = None

        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 1 and "toggle" in row.text:
                current_kategori = row.text.strip()
            elif len(cols) == 4 and "href" in str(row):
                nama_paket_tag = cols[1].find("a")
                nama_paket = nama_paket_tag.text.strip() if nama_paket_tag else ""
                link = urljoin(base_url, nama_paket_tag["href"]) if nama_paket_tag else ""
                hps = cols[2].text.strip()
                akhir = cols[3].text.strip()
                data.append({
                    "LPSE": base_url,
                    "Kategori": current_kategori,
                    "Nama Paket": nama_paket,
                    "HPS": hps,
                    "Akhir Pendaftaran": akhir,
                    "Link": link,
                })
        return data
    except Exception:
        return []

lpse_list = read_lpse_list("daftar_lpse.txt")
st.write(f"Total LPSE ditemukan: {len(lpse_list)}")

all_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(scrape_lpse, lpse_list)
    for result in results:
        if result:
            all_data.extend(result)

if all_data:
    df = pd.DataFrame(all_data)
    st.dataframe(df)
else:
    st.warning("Tidak ada data berhasil diambil dari LPSE yang tersedia.")
