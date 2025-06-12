import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Fungsi untuk mengambil daftar LPSE dari file GitHub
def get_lpse_list(url):
    response = requests.get(url)
    lpse_sites = response.text.strip().split("\n")
    return lpse_sites

# Fungsi untuk melakukan scraping dari satu situs LPSE
def scrape_lpse_tender(lpse_url):
    page = requests.get(lpse_url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    tenders = []
    
    for tender in soup.find_all("div", class_="tender-item"):
        nama_paket = tender.find("h3").text.strip()
        hps = tender.find("span", class_="hps").text.strip()
        akhir_pendaftaran = tender.find("span", class_="deadline").text.strip()
        link_sumber = tender.find("a", class_="source-link")["href"]
        
        tenders.append([nama_paket, hps, akhir_pendaftaran, lpse_url + link_sumber])

    return tenders

# URL file daftar LPSE
github_url = "https://raw.githubusercontent.com/udipop/udipop-lpse/main/daftar_lpse.txt"
lpse_sites = get_lpse_list(github_url)

# Mengumpulkan data dari semua LPSE
all_tenders = []
for lpse in lpse_sites:
    all_tenders.extend(scrape_lpse_tender(lpse))

# Simpan ke CSV
df = pd.DataFrame(all_tenders, columns=["Nama Paket", "HPS", "Akhir Pendaftaran", "Link Sumber"])
df.to_csv("data_lpse.csv", index=False)

# Aplikasi Streamlit untuk menampilkan data
st.title("Data Tender LPSE")
st.dataframe(df)
