import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Scraper Tender LPSE", layout="wide")
st.title("📦 Scraper Tender LPSE Nasional (HPS > Rp200jt)")

# Load daftar domain LPSE dari file
def load_lpse_list(path='daftar_lpse.txt'):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def extract_tender_data(domain):
    url = f"https://{domain}/eproc4/"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        rows = soup.select("table tr")[1:]  # skip header
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue
            nama_paket = cols[1].text.strip()
            hps_str = cols[2].text.strip().replace('Rp', '').replace('.', '').replace(',', '.')
            try:
                hps = float(hps_str)
            except ValueError:
                hps = 0
            akhir_pendaftaran = cols[3].text.strip()
            if hps > 200_000_000:
                data.append({
                    'LPSE': domain,
                    'Nama Paket': nama_paket,
                    'HPS': f"Rp {hps:,.0f}".replace(',', '.'),
                    'Akhir Pendaftaran': akhir_pendaftaran
                })
        return data
    except Exception as e:
        st.warning(f"Gagal mengambil data dari {domain}: {e}")
        return []

# Load semua domain
lpse_domains = load_lpse_list()

# Tampilkan progress
results = []
progress = st.progress(0)
status = st.empty()

for i, domain in enumerate(lpse_domains):
    status.text(f"Mengambil data dari: {domain}")
    tender_data = extract_tender_data(domain)
    results.extend(tender_data)
    progress.progress((i + 1) / len(lpse_domains))

progress.empty()
status.empty()

# Tampilkan hasil jika ada
df = None
if results:
    import pandas as pd
    df = pd.DataFrame(results)
    df = df.sort_values(by='HPS', ascending=False)
    st.success(f"Ditemukan {len(df)} paket tender dengan HPS di atas Rp200 juta.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Tidak ada data tender yang ditemukan.")
