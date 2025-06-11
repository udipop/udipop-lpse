import requests
from bs4 import BeautifulSoup
import re

def parse_hps(hps_str):
    try:
        hps_clean = hps_str.replace("Rp", "").replace(".", "").replace(",", ".").strip()
        return float(hps_clean)
    except:
        return 0

def scrape_lpse(url):
    try:
        res = requests.get(f"{url}/eproc4", timeout=10)
        res.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(res.text, "lxml")
    rows = soup.select("tr.Pekerjaan_Konstruksi")

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue
        nama_paket = cols[1].get_text(strip=True)
        hps_str = cols[2].get_text(strip=True)
        akhir_pendaftaran = cols[3].get_text(strip=True)

        hps_value = parse_hps(hps_str)
        if hps_value >= 200_000_000:
            link_tag = cols[1].find("a")
            link = url + link_tag["href"] if link_tag else ""
            data.append({
                "LPSE": url,
                "Nama Paket": nama_paket,
                "HPS": hps_value,
                "Akhir Pendaftaran": akhir_pendaftaran,
                "Link": link
            })
    return data

def scrape_all_lpse(lpse_list_file="daftar_lpse.txt"):
    with open(lpse_list_file) as f:
        urls = [line.strip() for line in f if line.strip()]
    all_data = []
    for url in urls:
        all_data.extend(scrape_lpse(url))
    return all_data
