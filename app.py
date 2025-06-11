import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Fungsi bantu untuk membersihkan nilai HPS
def clean_hps(hps_raw):
    return re.sub(r'\.00$', '', hps_raw.replace(',00', ''))

# Fungsi scrap 1 halaman LPSE
def scrape_lpse(url):
    paket_list = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal akses {url}: {e}")
        return paket_list

    soup = BeautifulSoup(response.text, 'html.parser')

    # Cari semua div atau tr yang berisi paket
    rows = soup.find_all("div", class_="daftar-paket") or soup.find_all("tr")

    for row in rows:
        try:
            nama_paket = row.find("a").get_text(strip=True)

            hps_tag = row.find(string=re.compile("HPS")).parent
            hps_raw = hps_tag.get_text(strip=True)
            hps_clean = clean_hps(re.search(r"Rp\s?[\d\.,]+", hps_raw).group())

            akhir_tag = row.find(string=re.compile("Akhir Pendaftaran"))
            akhir_pendaftaran = akhir_tag.find_next().get_text(strip=True)

            paket_list.append({
                "Nama Paket": nama_paket,
                "HPS": hps_clean,
                "Akhir Pendaftaran": akhir_pendaftaran
            })
        except Exception:
            continue

    return paket_list

# Baca semua link dari file
with open("daftar_lpse.txt", "r") as file:
    urls = [line.strip() for line in file if line.strip()]

# Gabungkan semua data
all_data = []
for url in urls:
    print(f"Scraping: {url}")
    data = scrape_lpse(url)
    all_data.extend(data)

# Tampilkan hasil dalam DataFrame
df = pd.DataFrame(all_data)
print(df)

# Simpan sebagai CSV jika diinginkan
df.to_csv("hasil_scrape_lpse.csv", index=False)
