import requests
from bs4 import BeautifulSoup

url = "https://lpse.lkpp.go.id/eproc4/"
res = requests.get(url)
soup = BeautifulSoup(res.content, "html.parser")

for row in soup.select("div.card.card-primary > table > tbody > tr"):
    cols = row.find_all("td")
    if len(cols) >= 4:
        nama = cols[1].get_text(strip=True)
        hps = cols[2].get_text(strip=True)
        akhir = cols[3].get_text(strip=True)
        print(nama, hps, akhir)
