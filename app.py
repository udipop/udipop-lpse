import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("📦 Tender Aktif di LPSE PUPR")
st.markdown("Menampilkan data tender aktif dari beranda utama [lpse.pu.go.id](https://lpse.pu.go.id/) dengan HPS ≥ Rp 200 juta.")

URL = "https://lpse.pu.go.id/"

@st.cache_data
def scrape_from_homepage():
    res = requests.get(URL)
    soup = BeautifulSoup(res.content, "html.parser")
    data = []

    for row in soup.select("tr[class]"):
        cols = row.find_all("td")
        if len(cols) != 4:
            continue

        link_tag = cols[1].find("a")
        if not link_tag:
            continue

        nama = link_tag.text.strip()
        hps = cols[2].text.strip()
        akhir = cols[3].text.strip()

        # parsing angka
        hps_val = hps.replace("Rp.", "").replace(".", "").replace(",", ".").strip()
        try:
            hps_float = float(hps_val)
        except:
            hps_float = 0

        if hps_float >= 200_000_000:
            data.append({
                "Nama Paket": nama,
                "HPS": hps,
                "Akhir Pendaftaran": akhir,
                "Link Sumber": URL  # selalu arahkan ke beranda
            })

    return pd.DataFrame(data)

df = scrape_from_homepage()

if df.empty:
    st.info("Tidak ada data tender aktif dengan HPS ≥ Rp 200 juta.")
else:
    df["Link"] = df["Link Sumber"].apply(lambda u: f'<a href="{u}" target="_blank">🔗 Lihat</a>')
    st.markdown(df[["Nama Paket", "HPS", "Akhir Pendaftaran", "Link"]].to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.caption("Sumber: lpse.pu.go.id — scraper oleh @udipop")
