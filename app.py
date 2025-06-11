import streamlit as st

st.set_page_config(page_title="LPSE Tender Viewer", layout="wide")

st.title("📄 Daftar Domain LPSE SPSE v4.x")

# Baca file daftar
try:
    with open("daftar_lpse.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
except FileNotFoundError:
    st.error("File daftar_lpse.txt tidak ditemukan.")
    st.stop()

# Konversi jadi tabel
data = [{"No": i+1, "Domain": line.strip()} for i, line in enumerate(lines) if line.strip()]
st.dataframe(data, use_container_width=True)
