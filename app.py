import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL GitHub langsung ke raw daftar LPSE
LPSE_LIST_URL = "https://raw.githubusercontent.com/udipop/udipop-lpse/main/daftar_lpse.txt"

# Fungsi ambil daftar LPSE
@st.cache_data
def get_lpse_list():
    response = requests.get(LPSE_LIST_URL)
    response.raise_for_status()
    return [line.strip() for line in response.text.splitlines() if line.strip()]

# Fungsi konversi HPS ke nilai numerik
def parse_hps(hps_text):
    try:
        hps_text = hps_text.replace(".", "").replace(",", ".")
        angka = ''.join(c for c in hps_text if c.isdigit() or c in ",.")
        return float(angka)
    except:
        return 0.0

# Fungsi scrap dari 1 situs LPSE
def scrape_lpse(lpse_url):
    base_url = f"https://{lpse_url}"
    tender_url = f"{base_url}/eproc4/lelang"
    tenders = []

    try:
        res = requests.get(tender_url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        rows = soup.select("table.table tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            nama_paket = cols[1].get_text(strip=True)
            link_detail = cols[1].find("a")["href"]
            hps = cols[3].get_text(strip=True)
            akhir_pendaftaran = cols[4].get_text(strip=True)

            hps_value = parse_hps(hps)
            if hps_value >= 200_000_000:
                tenders.append({
                    "Nama Paket": nama_paket,
                    "HPS": f"Rp {hps}",
                    "Akhir Pendaftaran": akhir_pendaftaran,
                    "Link Sumber": f"{base_url}{link_detail}",
                    "Situs LPSE": lpse_url
                })
    except Exception as e:
        st.warning(f"Gagal mengakses {lpse_url}: {e}")

    return tenders

# Judul Aplikasi
st.title("📦 Scraper Tender LPSE Nasional")
st.markdown("Menampilkan tender aktif dengan HPS ≥ Rp 200 juta dari berbagai situs LPSE.")

lpse_list = get_lpse_list()

all_tenders = []
progress = st.progress(0)
status = st.empty()

for idx, lpse in enumerate(lpse_list):
    status.text(f"Memproses: {lpse} ({idx+1}/{len(lpse_list)})")
    all_tenders.extend(scrape_lpse(lpse))
    progress.progress((idx + 1) / len(lpse_list))

progress.empty()
status.empty()

# Tampilkan hasil
if all_tenders:
    df = pd.DataFrame(all_tenders)

    # Tambah link klikable
    df["Link"] = df["Link Sumber"].apply(lambda url: f'<a href="{url}" target="_blank">🔗 Lihat</a>')
    df_display = df[["Nama Paket", "HPS", "Akhir Pendaftaran", "Link"]].to_html(escape=False, index=False)

    st.markdown("### 📋 Hasil Tender")
    st.markdown(df_display, unsafe_allow_html=True)
else:
    st.info("Tidak ada tender aktif dengan HPS ≥ Rp 200 juta yang ditemukan.")

st.markdown("---")
st.caption("Data real-time dari LPSE nasional. Dibuat oleh [@udipop](https://github.com/udipop)")
