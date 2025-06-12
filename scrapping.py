from selenium import webdriver, __version__ as seleniumVersion
from webdriver_manager.chrome import ChromeDriverManager as driverManager
from selenium.webdriver.chrome.service import Service as service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions as seleniumError
from bs4 import BeautifulSoup as bs
from requests import get, exceptions as exReq
from pprint import pprint
from re import sub, findall
from locale import localeconv
from datetime import datetime as dt
from pandas import (
    DataFrame,
    ExcelWriter,
    to_datetime as pdDateTime,
    to_numeric as pdNum,
)
from urllib3 import disable_warnings, exceptions as exUrl
from socket import gethostbyname, timeout

disable_warnings(
    category=(
        exUrl.InsecureRequestWarning,
        exUrl.NewConnectionError,
        exUrl.MaxRetryError,
        exUrl.HTTPError,
        exUrl.HTTPWarning,
    )
)


def durasi(app_start):
    app_stop = dt.now()
    selisih = app_stop - app_start
    getDurasi = divmod(selisih.seconds, 60)
    durasi = f"Time duration: {getDurasi[0]} minutes {getDurasi[1]} seconds"

    return durasi


def isLinkUp(url):
    patHttp = r"https?://"
    patBlock = r"Forbidden|Block"
    host = sub(patHttp, "", url)
    useHTTP = f"http://{host}"

    data = dict(status="", url=url, html="")

    try:
        # User https protocol
        req = get(url, timeout=5)
        if findall(patBlock, req.reason):
            try:
                req = get(useHTTP, timeout=5)
                data["status"] = "Up, use http"
                data["url"] = useHTTP
                data["html"] = bs(req.text, "html.parser")
            except:
                # 403 Forbidden
                data["status"] = "Blocked"
        else:
            data["status"] = "Up, use https"
            data["html"] = bs(req.text, "html.parser")
    except exReq.SSLError:
        # Use http protocol
        try:
            req = get(url, timeout=5, verify=False)
            data["status"] = "Up, use http"
            data["url"] = useHTTP
            data["html"] = bs(req.text, "html.parser")
        except:
            # Maybe blocked by AV
            data["status"] = "Blocked"
    except exReq.ConnectionError:
        try:
            # Use direct IP
            ip = f"http://{gethostbyname(host)}"
            req = get(ip, timeout=5)
            data["status"] = "Up, use IPv4"
            data["url"] = ip
            data["html"] = bs(req.text, "html.parser")
        except:
            data["status"] = "Error"
    except exReq.ReadTimeout:
        data["status"] = "Timeout"
    except Exception as e:
        data["status"] = e

    return data


def selenium():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--window-size=800x600")
    options.add_argument("--log-level=0")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")

    driver = webdriver.Chrome(
        service=service(driverManager().install()), options=options
    )

    return driver


def seleniumWait(driver, name):
    WebDriverWait(driver, 10).until(
        condition.presence_of_element_located((By.CLASS_NAME, name))
    )


def seleniumKodeTender(url, tahun):
    host = isLinkUp(url)
    if host["status"] in ["Error", "Timeout", "Blocked"]:
        print(f'URL {host["status"]}')
        return []
    else:
        try:
            web = selenium()

            # Open Link
            web.get(f"{host['url']}/eproc4/lelang")

            # Waiting element if exist then filter data
            seleniumWait(web, "dataTables_length")
            web.find_element(
                By.XPATH, f'//select[@name="tahun"]/option[text()="{tahun}"]'
            ).click()

            # Then show All Data
            web.find_element(
                By.XPATH, '//select[@name="tbllelang_length"]/option[text()="Semua"]'
            ).click()

            # Get Kode Tender
            seleniumWait(web, "sorting_1")
            id = web.find_elements(By.CLASS_NAME, "sorting_1")

            kodeTender = []
            for i in id:
                kodeTender.append(i.text)

            # web.close()
            # web.quit()

            return kodeTender
        except seleniumError.WebDriverException as e:
            print("URL Failed to Open")
            return []
        except Exception as e:
            print(e)
            return []


def getIP(url):
    regex = r"https?://"
    ip = gethostbyname(sub(regex, "", url))
    i = f"http://{ip}"
    return i


def request(url):
    try:
        try:
            req = get(url, timeout=10)
            return bs(req.text, "html.parser")
        except Exception as e:
            try:
                req = get(url, timeout=10, verify=False)
                return bs(req.text, "html.parser")
            except:
                return bs(req.text, "html.parser")
    except Exception as e:
        print("URL Failed to Open", e)


def soupPengumuman(html, text, tagName="td", index=0):
    try:
        findText = html.find_all(lambda tag: tag.name == "tr" and text in tag.text)[0]
        result = findText.find_all(tagName)[index].string
        return result
    except:
        return ""


def soupPemenang(html, index):
    try:
        findText = html.find_all("table")[0].find_all("table")[0].find_all("tr")[1]
        result = findText.find_all("td")[index].text
        return result
    except:
        return ""


def cleanTxt(text):
    return sub(r"\n|\xa0|[.]", "", text.strip())


def cleanNum(text):
    getLocalDecimal = localeconv()["decimal_point"]
    setDecimal = "." if getLocalDecimal == "." else ","
    txt = sub(r"\n|Rp. |[.]", "", text)
    result = "" if text == " - " else txt.replace(",", f"{setDecimal}")
    return result


def autoDate(txt):
    month = {
        "Januari": 1,
        "Februari": 2,
        "Maret": 3,
        "April": 4,
        "Mei": 5,
        "Juni": 6,
        "Juli": 7,
        "Agustus": 8,
        "September": 9,
        "Oktober": 10,
        "November": 11,
        "Desember": 12,
    }

    try:
        n = txt.strip().split(" ")
        date = (
            dt.strptime(f"{n[0]}-{month[n[1]]}-{n[2]}", "%d-%m-%Y")
            .date()
            .strftime("%d-%m-%Y")
        )
        return date
    except:
        return txt


# "http://lpse.pidiekab.go.id/eproc4/lelang/4999565/pengumumanlelang"
# "https://lpse.acehsingkilkab.go.id/eproc4/evaluasi/3026508/pemenang"


def soupLpse(url, id):

    host = isLinkUp(url)

    link = f"{host['url']}/eproc4/lelang/{id}/pengumumanlelang"
    link2 = f"{host['url']}/eproc4/evaluasi/{id}/pemenang"

    # Get Pengumuman
    lpse = isLinkUp(link)["html"]

    label = soupPengumuman(lpse, "Nama Tender", "span")
    nama = soupPengumuman(lpse, "Nama Tender", "strong")
    tanggal = soupPengumuman(lpse, "Tanggal Pembuatan")
    tahap = soupPengumuman(lpse, "Tahap Tender")
    klpd = soupPengumuman(lpse, "K/L/PD")
    satker = soupPengumuman(lpse, "Satuan Kerja")
    jenis = soupPengumuman(lpse, "Jenis Pengadaan")
    metode = soupPengumuman(lpse, "Metode Pengadaan")
    tahun = soupPengumuman(lpse, "Tahun Anggaran")
    pagu = soupPengumuman(lpse, "Nilai Pagu")
    hps = soupPengumuman(lpse, "Nilai HPS", "td", 1)
    kontrak = soupPengumuman(lpse, "Jenis Kontrak")
    lokasi = soupPengumuman(lpse, "Lokasi Pekerjaan", "li")
    kualifikasi = soupPengumuman(lpse, "Kualifikasi Usaha")

    lpse = dict(
        link_lpse=link,
        label_paket=label,
        nama_tender=nama,
        tanggal_pembuatan=autoDate(tanggal),
        tahap_tender_saat_ini=tahap,
        klpd=cleanTxt(klpd),
        satuan_kerja=satker,
        jenis_pengadaan=jenis,
        metode_pengadaan=metode,
        tahun_anggaran=cleanTxt(tahun),
        nilai_pagu_paket=cleanNum(pagu),
        nilai_hps_paket=cleanNum(hps),
        jenis_kontrak=kontrak,
        lokasi_pekerjaan=lokasi,
        kualifikasi_usaha=kualifikasi,
        nama_pemenang="",
        alamat="",
        npwp="",
        harga_penawaran="",
        harga_terkoreksi="",
        hasil_negosiasi="",
        harga_negosiasi="",
    )

    # Get Pemenang Tender
    tender = isLinkUp(link2)["html"]

    lpse["nama_pemenang"] = soupPemenang(tender, 0)
    lpse["alamat"] = soupPemenang(tender, 1)
    lpse["npwp"] = cleanTxt(soupPemenang(tender, 2))
    lpse["harga_penawaran"] = cleanNum(soupPemenang(tender, 3))
    lpse["harga_terkoreksi"] = cleanNum(soupPemenang(tender, 4))
    lpse["hasil_negosiasi"] = cleanNum(soupPemenang(tender, 6))
    lpse["harga_negosiasi"] = cleanNum(soupPemenang(tender, 5))

    return lpse


def clear_line():
    from os import system
    from sys import stdout

    stdout.write("\033[F")  # back to previous line
    stdout.write("\033[K")  # clear line


start = dt.now()
url = "https://lpse.belitungtimurkab.go.id"
# "https://lpse.acehsingkilkab.go.id"

kodeTender = seleniumKodeTender(url, 2022)

lpse = []
total = len(kodeTender)
n = 0

if kodeTender == []:
    print("data kosong")
else:
    # start
    for kode in kodeTender:
        # break
        n = n + 1
        print(f"{n}/{total}")
        clear_line()
        lpse.append(soupLpse(url, kode))

        # DataFrame
        df = DataFrame(lpse)
        df["tanggal_pembuatan"] = pdDateTime(
            df["tanggal_pembuatan"], dayfirst=True
        ).dt.date

        ToFloat = [
            "nilai_pagu_paket",
            "nilai_hps_paket",
            "harga_penawaran",
            "harga_terkoreksi",
            "hasil_negosiasi",
            "harga_negosiasi",
        ]
        df[ToFloat] = df[ToFloat].apply(pdNum, errors="coerce")

        # Export to Excel
        lpseName = url.split(".")[1]
        fileName = f"lpse_{lpseName}_.xlsx"

        excel = ExcelWriter(fileName, "openpyxl")
        df.to_excel(excel, index=False)
        # excel.book.set_properties({'author': 'seimpairiyun'}) #xlsxwriter
        excel.book.properties.creator = "seimpairiyun"
        excel.close()

print(durasi(start))
# print(lpse)
