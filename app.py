import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://lpse.lkpp.go.id/eproc4/"

st.set_page_config(page_title="Tender LPSE LKPP", layout="wide")
st.title("📦 Data Tender Aktif – LPSE LKPP")
st.markdown(f"Menampilkan informasi tender dari halaman utama: [lpse.lkpp.go.id](https://lpse.lkpp.go.id/eproc4/)")

@st.cache_data(ttl=600)
def scrape_lpse_lkpp():
    try:
        res = requests.get(URL, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        data = []
        rows = soup.select("div.card.card-primary > table > tbody > tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            link_tag = cols[1].find("a")
            if not link_tag:
                continue

            nama_paket = link_tag.text.strip()
            hps = cols[2].text.strip()
            akhir = cols[3].text.strip()

            data.append({
                "Nama Paket": nama_paket,
                "HPS": hps,
                "Akhir Pendaftaran": akhir,
                "Link Sumber": URL
            })

        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return pd.DataFrame()

df = scrape_lpse_lkpp()

if df.empty:
    st.info("Tidak ada data tender ditemukan.")
else:
    df["Link"] = df["Link Sumber"].apply(lambda u: f'<a href="{u}" target="_blank">🔗 Lihat</a>')
    st.markdown(df[["Nama Paket", "HPS", "Akhir Pendaftaran", "Link"]].to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.caption("Data dari LPSE LKPP – disajikan oleh @udipop")
