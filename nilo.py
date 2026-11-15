import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import urllib3
import warnings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

GITHUB_URL = "https://raw.githubusercontent.com/koprulu555/selcuk-full-domain-kontrol/refs/heads/main/selcuk_sports_guncel_domain.txt"
OUTPUT_FILENAME = "channels.m3u"

def get_active_domain_from_github():
    print("--- 📡 GitHub üzerinden güncel domain alınıyor ---")
    try:
        req = Request(GITHUB_URL, headers=HEADERS)
        html = urlopen(req, timeout=10).read().decode()
        match = re.search(r'selcuk_guncel_domain=(https?://[^\s\b]+)', html)
        if match:
            domain = match.group(1).strip().rstrip('/')
            print(f"✅ Aktif Domain: {domain}")
            return domain
    except Exception as e:
        print(f"❌ GitHub okuma hatası: {e}")
    return "https://www.selcuksportshd14e17ba2ad.xyz"

def fetch_html_with_proxy(url):
    proxy_url = "https://api.codetabs.com/v1/proxy/?quest="
    try:
        req = Request(url, headers=HEADERS)
        return urlopen(req, timeout=10).read().decode()
    except Exception:
        try:
            req = Request(f"{proxy_url}{url}", headers=HEADERS)
            return urlopen(req, timeout=10).read().decode()
        except Exception as e:
            print(f"❌ Proxy bağlantı hatası: {e}")
            return None

def build_m3u():
    active_domain = get_active_domain_from_github()
    referer = f"{active_domain}/"
    
    print(f"🔍 Ana sayfa taraniyor...")
    html_content = fetch_html_with_proxy(active_domain)
    if not html_content:
        print("❌ Ana sayfa içeriği alınamadı.")
        return

    # Sayfadaki tüm .click domainlerini bul
    click_domains = re.findall(r'https?://[a-zA-Z0-9.-]+\.click', html_content)
    
    origin_domain = None
    stream_cdn = None

    # 1. UXSYPlayer kök adresini bul (ORIGIN için)
    for d in click_domains:
        if "uxsyplayer" in d:
            origin_domain = d
            break

    # 2. Gerçek Stream CDN adresini bul (AMP OLMAYAN ve uxsyplayer OLMAYAN .click adresini seç)
    for d in click_domains:
        if "uxsyplayer" not in d and "amp" not in d:
            stream_cdn = d
            break

    # Fallback / Emniyet Sübapları
    if not origin_domain:
        origin_domain = "https://main.uxsyplayer6859599e6c.click"
    if not stream_cdn:
        # Eğer listede temiz cdn yoksa bilinen kararlı cdn kökünü kullan
        stream_cdn = "https://dga1op10s1u3lea.aae77b66b9d557.click"

    print(f"🎯 Kesinleşen ORIGIN: {origin_domain}")
    print(f"🎯 Kesinleşen STREAM_CDN: {stream_cdn}")

    soup = BeautifulSoup(html_content, "html.parser")
    links = []

    for a in soup.find_all(attrs={"data-url": True}):
        data_url = a["data-url"].strip()
        name = a.text.strip()
        if data_url:
            if data_url.startswith("/"):
                data_url = active_domain + data_url
            links.append({"url": data_url, "name": name if name else "Kanal"})

    if not links:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            name = a.text.strip()
            if "id=" in href or "match" in href or "channel" in href:
                if href.startswith("/"):
                    href = active_domain + href
                links.append({"url": href, "name": name if name else "Kanal"})

    print(f"📺 Toplam {len(links)} yayın işleniyor...")

    ua = HEADERS["User-Agent"]
    m3u_lines = ["#EXTM3U"]
    ok = 0
    seen = set()

    for ch in links:
        player_url = ch["url"]
        
        # Stream ID'yi hassas bir şekilde çek
        stream_id = None
        m_id = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", player_url)
        if m_id:
            stream_id = m_id.group(1)
        else:
            parts = [p for p in player_url.split('/') if p and not p.startswith('http')]
            if parts:
                potential_id = parts[-1].split('?')[0]
                if potential_id and potential_id not in ('index.html', 'index.php', 'embed.php', 'amp.html'):
                    stream_id = potential_id

        if not stream_id or "html" in stream_id.lower() or "undefined" in stream_id.lower() or stream_id == "selcukahaber":
            continue

        # Doğru ve temiz Stream CDN ile m3u8 adresini oluştur
        m3u8 = f"{stream_cdn.rstrip('/')}/live/{stream_id}/playlist.m3u8"

        if m3u8 in seen:
            continue
        seen.add(m3u8)

        display_name = ch["name"]

        # Tam istediğiniz başlık ve etiket sıralaması
        entry = (
            f'#EXT-X-USER-AGENT:{ua}\n'
            f'#EXT-X-REFERER:{referer}\n'
            f'#EXT-X-ORIGIN:{origin_domain}\n'
            f'#EXTVLCOPT:http-user-agent={ua}\n'
            f'#EXTVLCOPT:http-referrer={referer}\n'
            f'#EXTVLCOPT:http-origin={origin_domain}\n'
            f'#EXTINF:-1 tvg-name="{display_name}" group-title="nilo",{display_name}\n'
            f'{m3u8}'
        )
        m3u_lines.append(entry)
        ok += 1

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"\n✅ M3U başarıyla oluşturuldu: {OUTPUT_FILENAME}")
    print(f"📊 Eklenen Çalışan Yayın Sayısı: {ok}")

if __name__ == "__main__":
    build_m3u()
