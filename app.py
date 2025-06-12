import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Tender LPSE PUPR", layout="wide")
st.title("📦 Tender Aktif di LPSE PUPR")
st.markdown("Menampilkan data tender aktif dari halaman [lpse.pu.go.id/eproc4/lelang](https://lpse.pu.go.id/eproc4/lelang) dengan HPS ≥ Rp 200 juta.")

LELANG_URL = "https://lpse.pu.go.id/eproc4/lelang"
LINK_SITUS = "https://lpse.pu.go.id/"

@st.cache_data(ttl=1800)
def scrape_tender_lpse():
    res = requests.get(LELANG_URL, timeout=10)
    soup = BeautifulSoup(res.content, "html.parser")
    data = []

    for row in soup.select("table.table tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        nama_tag = cols[1].find("a")
        if not nama_tag:
            continue

        nama_paket = nama_tag.text.strip()
        hps = cols[3].text.strip()
        akhir = cols[4].text.strip()

        # Ubah HPS ke angka numerik
        hps_val = hps.replace("Rp", "").replace(".", "").replace(",", ".").strip()
        try:
            hps_float = float(hps_val)
        except:
            hps_float = 0

        if hps_float >= 200_000_000:
            data.append({
                "Nama Paket": nama_paket,
                "HPS": hps,
                "Akhir Pendaftaran": akhir,
                "Link Sumber": LINK_SITUS
            })

    return pd.DataFrame(data)

df = scrape_tender_lpse()

if df.empty:
    st.info("Tidak ada data tender aktif dengan HPS ≥ Rp 200 juta.")
else:
    df["Link"] = df["Link Sumber"].apply(lambda url: f'<a href="{url}" target="_blank">🔗 Lihat</a>')
    st.markdown(df[["Nama Paket", "HPS", "Akhir Pendaftaran", "Link"]].to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.caption("Sumber: lpse.pu.go.id — scraper oleh @udipop")
