import os
import re
import json
import time
import logging
import requests as req_lib
from datetime import datetime

# ── Sabitler ──────────────────────────────────────────
DOMAIN_TIMEOUT = 3
MIN_NUMBER     = 49
MAX_NUMBER     = 75
DOMAIN_BASE    = "mahsunsports"
DOMAIN_TLD     = "xyz"
OUTPUT_FILE    = "mike.m3u"
STATS_FILE     = "stats.json"

# ── Logging ───────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# ── Kanal Listesi ─────────────────────────────────────
CHANNELS = [
    {"slug": "androstreamlivebs1",     "name": "BeIN Sports 1",       "group": "Spor"},
    {"slug": "androstreamlivebs2",     "name": "BeIN Sports 2",       "group": "Spor"},
    {"slug": "androstreamlivebs3",     "name": "BeIN Sports 3",       "group": "Spor"},
    {"slug": "androstreamlivebs4",     "name": "BeIN Sports 4",       "group": "Spor"},
    {"slug": "androstreamlivebs5",     "name": "BeIN Sports 5",       "group": "Spor"},
    {"slug": "androstreamlivebsm1",    "name": "BeIN Sports Max 1",   "group": "Spor"},
    {"slug": "androstreamlivebsm2",    "name": "BeIN Sports Max 2",   "group": "Spor"},
    {"slug": "androstreamlivess1",     "name": "S Sport",             "group": "Spor"},
    {"slug": "androstreamlivess2",     "name": "S Sport 2",           "group": "Spor"},
    {"slug": "androstreamlivessplus1", "name": "S Sport Plus",        "group": "Spor"},
    {"slug": "androstreamlivets",      "name": "Tivibu Spor",         "group": "Spor"},
    {"slug": "androstreamlivets1",     "name": "Tivibu Spor 1",       "group": "Spor"},
    {"slug": "androstreamlivets2",     "name": "Tivibu Spor 2",       "group": "Spor"},
    {"slug": "androstreamlivets3",     "name": "Tivibu Spor 3",       "group": "Spor"},
    {"slug": "androstreamlivets4",     "name": "Tivibu Spor 4",       "group": "Spor"},
    {"slug": "androstreamlivesm1",     "name": "Smart Spor 1",        "group": "Spor"},
    {"slug": "androstreamlivesm2",     "name": "Smart Spor 2",        "group": "Spor"},
    {"slug": "androstreamlivees1",     "name": "Euro Sport 1",        "group": "Spor"},
    {"slug": "androstreamlivees2",     "name": "Euro Sport 2",        "group": "Spor"},
    {"slug": "androstreamliveidm",     "name": "iDMAN Tv",            "group": "Spor"},
    {"slug": "androstreamlivetrts",    "name": "TRT Spor",            "group": "Spor"},
    {"slug": "androstreamlivetrtsy",   "name": "TRT Spor Yıldız",     "group": "Spor"},
    {"slug": "androstreamlivetrts1",   "name": "TRT 1",               "group": "Genel"},
    {"slug": "androstreamliveatv",     "name": "Atv",                 "group": "Genel"},
    {"slug": "androstreamliveas",      "name": "A Spor",              "group": "Spor"},
    {"slug": "androstreamlivea2",      "name": "A2",                  "group": "Genel"},
    {"slug": "androstreamlivetjk",     "name": "Tjk Tv",              "group": "Spor"},
    {"slug": "androstreamliveht",      "name": "Ht Spor",             "group": "Spor"},
    {"slug": "androstreamlivenba",     "name": "NBA Tv",              "group": "Spor"},
    {"slug": "androstreamlivetv8",     "name": "TV8",                 "group": "Genel"},
    {"slug": "androstreamlivetv85",    "name": "TV8,5",               "group": "Genel"},
    {"slug": "androstreamlivetb",      "name": "Tabi Spor",           "group": "Spor"},
    {"slug": "androstreamlivetb1",     "name": "Tabi Spor 1",         "group": "Spor"},
    {"slug": "androstreamlivetb2",     "name": "Tabi Spor 2",         "group": "Spor"},
    {"slug": "androstreamlivetb3",     "name": "Tabi Spor 3",         "group": "Spor"},
    {"slug": "androstreamlivetb4",     "name": "Tabi Spor 4",         "group": "Spor"},
    {"slug": "androstreamlivetb5",     "name": "Tabi Spor 5",         "group": "Spor"},
    {"slug": "androstreamlivetb6",     "name": "Tabi Spor 6",         "group": "Spor"},
    {"slug": "androstreamlivetb7",     "name": "Tabi Spor 7",         "group": "Spor"},
    {"slug": "androstreamlivetb8",     "name": "Tabi Spor 8",         "group": "Spor"},
    {"slug": "androstreamlivefb",      "name": "FB Tv",               "group": "Spor"},
    {"slug": "androstreamlivegs",      "name": "GS Tv",               "group": "Spor"},
    {"slug": "androstreamlivecbcs",    "name": "CBC Sport",           "group": "Spor"},
    {"slug": "androstreamlivesptstv",  "name": "Sports Tv",           "group": "Spor"},
    {"slug": "androstreamliveexn",     "name": "Exxen Tv",            "group": "Spor"},
    {"slug": "androstreamliveexn1",    "name": "Exxen Sports 1",      "group": "Spor"},
    {"slug": "androstreamliveexn2",    "name": "Exxen Sports 2",      "group": "Spor"},
    {"slug": "androstreamliveexn3",    "name": "Exxen Sports 3",      "group": "Spor"},
    {"slug": "androstreamliveexn4",    "name": "Exxen Sports 4",      "group": "Spor"},
    {"slug": "androstreamliveexn5",    "name": "Exxen Sports 5",      "group": "Spor"},
    {"slug": "androstreamliveexn6",    "name": "Exxen Sports 6",      "group": "Spor"},
    {"slug": "androstreamliveexn7",    "name": "Exxen Sports 7",      "group": "Spor"},
    {"slug": "androstreamliveexn8",    "name": "Exxen Sports 8",      "group": "Spor"},
]


def find_base_url():
    session = req_lib.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    log.info(f"🔎 Domain taranıyor: {DOMAIN_BASE}{MIN_NUMBER}.{DOMAIN_TLD} → {DOMAIN_BASE}{MAX_NUMBER}.{DOMAIN_TLD}")

    for i in range(MIN_NUMBER, MAX_NUMBER + 1):
        domain = f"https://{DOMAIN_BASE}{i}.{DOMAIN_TLD}"
        try:
            resp = session.get(domain, headers=headers, timeout=DOMAIN_TIMEOUT, allow_redirects=False, verify=False)
            if resp.status_code in (200, 301, 302, 303, 307, 308):
                final_url = domain.rstrip("/")
                log.info(f"  ✅ Aktif domain bulundu: {final_url}")
                return final_url
        except Exception:
            pass
    return f"https://{DOMAIN_BASE}50.{DOMAIN_TLD}"


def get_active_server(base_url):
    event_url = f"{base_url}/event.html?id=androstreamlivebs1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"{base_url}/"
    }
    try:
        resp = req_lib.get(event_url, headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            match = re.search(r'baseurls\s*=\s*\[(.*?)\]', resp.text, re.DOTALL | re.IGNORECASE)
            if match:
                urls_text = match.group(1).replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
                servers = [u.strip() for u in urls_text.split(',') if u.strip().startswith("http")]
                
                for server in servers:
                    server = server.rstrip('/')
                    test_url = f"{server}/androstreamlivebs1.m3u8" if "checklist" in server else f"{server}/checklist/androstreamlivebs1.m3u8"
                    test_url = test_url.replace("checklist//", "checklist/")
                    try:
                        t_res = req_lib.get(test_url, headers={'Referer': base_url + "/"}, timeout=5, verify=False)
                        if t_res.status_code == 200:
                            return server
                    except Exception:
                        continue
                if servers:
                    return servers[0].rstrip('/')
    except Exception as e:
        log.error(f"Sunucu listesi alınamadı: {e}")
    
    # Yedek sunucu kökü (Bulunamazsa patlamaması için)
    return "https://andro.evrenesoglu235.click"


def create_m3u(channels):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "#EXTM3U\n",
        f"# Site      : mahsunsports\n",
        f"# Güncelleme: {now}\n",
        f"# Toplam    : {len(channels)} kanal\n\n",
    ]
    for ch in channels:
        extinf  = '#EXTINF:-1'
        extinf += f' tvg-name="{ch["name"]}"'
        extinf += f' group-title="{ch["group"]}"'
        extinf += f',{ch["name"]}\n'
        lines.append(extinf)
        lines.append(f'{ch["url"]}\n\n')
    return "".join(lines)


def main():
    log.info("=" * 55)
    log.info("   M3U8 Generator (Tek Dosya Modu) → MAHSUNSPORTS")
    log.info("=" * 55)

    start = time.time()
    base_url = find_base_url()
    log.info(f"🌐 BASE_URL: {base_url}")

    active_server = get_active_server(base_url)
    log.info(f"🎯 Aktif yayın sunucusu: {active_server}")

    channels = []
    for page in CHANNELS:
        cid = page["slug"].replace("event.html?id=", "")
        furl = f"{active_server}/{cid}.m3u8" if "checklist" in active_server else f"{active_server}/checklist/{cid}.m3u8"
        furl = furl.replace("checklist//", "checklist/")

        channels.append({
            "name": page["name"],
            "url": furl,
            "group": page["group"]
        })

    elapsed = round(time.time() - start, 1)

    # mike.m3u dosyasını her koşulda garanti yaz
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(create_m3u(channels))

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "site"           : "mahsunsports",
            "last_update"    : datetime.now().isoformat(),
            "base_url"       : base_url,
            "active_server"  : active_server,
            "total_channels" : len(channels),
            "duration_sec"   : elapsed,
            "channels"       : channels
        }, f, ensure_ascii=False, indent=2)

    log.info(f"🏁 İşlem Tamamlandı! '{OUTPUT_FILE}' dosyasına toplam {len(channels)} kanal yazıldı ({elapsed}s)")


if __name__ == "__main__":
    main()
