import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("📋 Udipop Scraper Tender LPSE Indonesia")

def get_tender_data(lpse_url):
    try:
        response = requests.get(f"{lpse_url}/eproc4", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select("div.card.card-primary table tbody tr")
        data = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue
            link_tag = cols[1].find('a')
            nama_paket = link_tag.text.strip() if link_tag else cols[1].text.strip()
            link = lpse_url + link_tag.get("href") if link_tag else lpse_url
            hps = cols[2].text.strip()
            akhir_pendaftaran = cols[3].text.strip()
            data.append({
                "Nama Paket": nama_paket,
                "HPS": hps,
                "Akhir Pendaftaran": akhir_pendaftaran,
                "Sumber": link
            })
        return data
    except Exception as e:
        return []

def main():
    st.title("Scraper Tender LPSE Seluruh Indonesia")

    with open("daftar_lpse.txt", "r") as f:
        lpse_links = [line.strip() for line in f.readlines() if line.strip()]

    selected_lpse = st.selectbox("Pilih LPSE", lpse_links)
    st.write(f"Menampilkan data dari: {selected_lpse}")

    with st.spinner("Mengambil data..."):
        result = get_tender_data(selected_lpse)

    if result:
        df = pd.DataFrame(result)
        df["Sumber"] = df["Sumber"].apply(lambda x: f"[Lihat]({x})")
        st.write(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data ditemukan atau terjadi kesalahan.")

if __name__ == "__main__":
    main()
