import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(layout="wide")
st.title("📦 Tender LPSE Scraper")

HPS_MINIMUM = 200_000_000

@st.cache_data(show_spinner=False)
def get_lpse_links():
    try:
        with open("daftar_lpse.txt", "r") as file:
            return [line.strip().rstrip("/") for line in file if line.strip()]
    except FileNotFoundError:
        return []

@st.cache_data(show_spinner="🔍 Mengambil data dari LPSE...")
def scrap_lpse(url):
    base_url = url + "/eproc4"
    try:
        res = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        table = soup.find("table")
        if not table:
            return []

        rows = table.select("tbody > tr")
        kategori = ""
        results = []

        for row in rows:
            if row.find("a") and "toggle();" in row.find("a").get("onclick", ""):
                kategori = row.get_text(strip=True)
                continue

            cols = row.find_all("td")
            if len(cols) == 4:
                nama_paket_tag = cols[1].find("a")
                nama_paket = nama_paket_tag.text.strip()
                link = base_url + nama_paket_tag.get("href") if nama_paket_tag else ""
                hps_str = cols[2].text.strip()
                akhir = cols[3].text.strip()

                hps = int(re.sub(r"[^0-9]", "", hps_str))

                if hps >= HPS_MINIMUM:
                    results.append({
                        "LPSE": url,
                        "Kategori": kategori,
                        "Nama Paket": nama_paket,
                        "HPS": hps,
                        "Akhir Pendaftaran": akhir,
                        "Link": link
                    })
        return results
    except Exception as e:
        st.warning(f"⚠️ Gagal mengakses {url}: {e}")
        return []

lpse_links = get_lpse_links()

if not lpse_links:
    st.error("❌ File 'daftar_lpse.txt' tidak ditemukan atau kosong.")
else:
    all_data = []
    for link in lpse_links:
        data = scrap_lpse(link)
        all_data.extend(data)

    if not all_data:
        st.info("🔍 Tidak ditemukan tender dengan HPS ≥ 200 juta.")
    else:
        df = pd.DataFrame(all_data)
        df = df.sort_values(by="HPS", ascending=False).reset_index(drop=True)
        df["HPS"] = df["HPS"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        st.dataframe(df, use_container_width=True)
