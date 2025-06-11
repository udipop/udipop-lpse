import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin

st.set_page_config(page_title="LPSE Tender Scraper", layout="wide")
st.title("📦 Tender LPSE Scraper")

MIN_HPS = 200_000_000

@st.cache_data(show_spinner=False)
def load_lpse_list(file_path="daftar_lpse.txt"):
    with open(file_path, "r") as f:
        return [line.strip().rstrip('/') for line in f if line.strip()]

def parse_rupiah_to_int(rupiah_str):
    try:
        cleaned = re.sub(r'[^0-9]', '', rupiah_str)
        return int(cleaned)
    except:
        return 0

def scrap_lpse(url):
    try:
        full_url = urljoin(url, "/eproc4")
        res = requests.get(full_url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return []  # Skip errors silently now

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table.table.table-sm tbody tr")

    current_category = ""
    tender_data = []

    for row in rows:
        if row.find("td", colspan=True):
            current_category = row.get_text(strip=True)
            continue

        cols = row.find_all("td")
        if len(cols) != 4:
            continue

        try:
            nama = cols[1].get_text(strip=True)
            hps = cols[2].get_text(strip=True)
            akhir = cols[3].get_text(strip=True)
            hps_int = parse_rupiah_to_int(hps)
            if hps_int >= MIN_HPS:
                link_tag = cols[1].find("a")
                if link_tag and link_tag.has_attr("href"):
                    link = urljoin(full_url, link_tag["href"])
                    tender_data.append({
                        "LPSE": url,
                        "Kategori": current_category,
                        "Nama Paket": nama,
                        "HPS": hps,
                        "Akhir Pendaftaran": akhir,
                        "Link": link
                    })
        except Exception:
            continue

    return tender_data

lpse_urls = load_lpse_list()

all_tenders = []
progress = st.progress(0, text="Scraping LPSE...")

for idx, lpse_url in enumerate(lpse_urls):
    tenders = scrap_lpse(lpse_url)
    all_tenders.extend(tenders)
    progress.progress((idx + 1) / len(lpse_urls), text=f"Memproses {idx + 1} dari {len(lpse_urls)} LPSE")

progress.empty()

if all_tenders:
    df = pd.DataFrame(all_tenders)
    df_sorted = df.sort_values(by="HPS", key=lambda col: col.map(parse_rupiah_to_int), ascending=False)
    st.success(f"Menampilkan {len(df_sorted)} tender dengan HPS ≥ Rp 200.000.000")
    st.dataframe(df_sorted.reset_index(drop=True))
else:
    st.warning("Tidak ada data tender yang memenuhi syarat atau semua koneksi gagal.")
