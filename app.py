import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.title("📋 Tender Aktif dari Seluruh LPSE SPSE v4.x")

# Fungsi untuk ambil tender dari satu domain
def ambil_tender(domain):
    url = f"{domain}/eproc4/lelang"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")[1:]  # Skip header
        hasil = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                hasil.append({
                    "LPSE": domain.replace("https://", ""),
                    "Kode Tender": cols[0].text.strip(),
                    "Nama Paket": cols[1].text.strip(),
                    "Satuan Kerja": cols[2].text.strip(),
                    "Tahapan": cols[3].text.strip()
                })
        return hasil
    except Exception as e:
        return [{"LPSE": domain.replace("https://", ""), "Kode Tender": "-", "Nama Paket": f"Gagal ambil data: {e}", "Satuan Kerja": "-", "Tahapan": "-"}]

# Baca daftar domain
with open("daftar_lpse.txt", "r") as f:
    list_domain = [line.strip() for line in f.readlines() if line.strip()]

st.write(f"📡 Mengambil tender aktif dari {len(list_domain)} domain LPSE...")

# Proses paralel agar cepat
all_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(ambil_tender, list_domain)
    for result in results:
        all_data.extend(result)

# Tampilkan data jika ada
if all_data:
    df = pd.DataFrame(all_data)
    st.success(f"Ditemukan {len(df)} data tender aktif!")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "tender_lpse.csv", "text/csv")
else:
    st.warning("Tidak ada data tender yang ditemukan.")
