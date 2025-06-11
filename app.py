import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Fungsi bersihkan HPS
def clean_hps(hps_raw):
    hps_raw = re.sub(r',00|\.00$', '', hps_raw)
    return hps_raw

# Fungsi scraping satu halaman
def scrape_lpse(url):
    paket_list = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"Gagal akses {url}: {e}")
        return paket_list

    soup = BeautifulSoup(response.text, 'html.parser')

    # Cari elemen paket
    paket_divs = soup.find_all('div', class_='col-md-9') or []
    for div in paket_divs:
        try:
            nama = div.find('a').get_text(strip=True)

            hps_text = div.find(string=re.compile('HPS'))
            hps_value = clean_hps(re.search(r'Rp\s[\d\.,]+', hps_text).group())

            akhir = div.find(string=re.compile('Akhir Pendaftaran'))
            akhir_value = akhir.find_next().get_text(strip=True)

            paket_list.append({
                "Nama Paket": nama,
                "HPS": hps_value,
                "Akhir Pendaftaran": akhir_value,
                "Sumber": url
            })
        except Exception:
            continue

    return paket_list

# === STREAMLIT UI ===
st.set_page_config(page_title="Scraper LPSE", layout="wide")
st.title("🛠️ Scraper LPSE dari daftar link")

uploaded_file = st.file_uploader("Upload file daftar_lpse.txt", type=['txt'])

if uploaded_file:
    urls = uploaded_file.read().decode('utf-8').splitlines()
    urls = [u.strip() for u in urls if u.strip()]
    
    all_data = []

    progress = st.progress(0)
    for i, url in enumerate(urls):
        st.write(f"🔗 Memproses: {url}")
        data = scrape_lpse(url)
        all_data.extend(data)
        progress.progress((i+1)/len(urls))

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"✅ Ditemukan {len(df)} paket dari {len(urls)} link")
        st.dataframe(df)
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="hasil_lpse.csv")
    else:
        st.error("❌ Tidak ada data yang berhasil diambil.")
