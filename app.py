import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def format_hps(hps):
    return re.sub(r',00$', '', hps.strip())

def scrape_lpse(url):
    try:
        page = requests.get(f"{url}/eproc4/lelang")
        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find('table', class_='table')

        rows = table.find_all('tr')[1:]  # skip header
        results = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            nama_paket = cols[1].text.strip()
            hps = format_hps(cols[3].text.strip())
            akhir_pendaftaran = cols[4].text.strip()
            link = url + cols[1].find('a')['href']
            results.append([nama_paket, hps, akhir_pendaftaran, link])
        return results
    except Exception as e:
        return [["Gagal scrap", str(e), "", url]]

# Streamlit UI
st.title("📦 Scraper LPSE dari daftar link")

uploaded_file = st.file_uploader("Upload file daftar_lpse.txt", type='txt')
if uploaded_file:
    urls = uploaded_file.getvalue().decode("utf-8").splitlines()
    all_data = []
    for url in urls:
        all_data += scrape_lpse(url.strip())

    df = pd.DataFrame(all_data, columns=["Nama Paket", "Nilai HPS", "Akhir Pendaftaran", "Link Sumber"])
    st.dataframe(df)
    st.success(f"Ditemukan {len(df)} tender.")
