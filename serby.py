import os
import re
import urllib.parse
import urllib3
import warnings
import requests

# --- CONFIGURATION ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
}
TIMEOUT_VAL = 15
PROXY_URL = "https://seep.eu.org/"  # Engelleri aşmak için proxy geri eklendi
GITHUB_DOMAIN_URL = "https://raw.githubusercontent.com/koprulu555/selcuk-full-domain-kontrol/refs/heads/main/selcuk_sports_guncel_domain.txt"
OUTPUT_FILENAME = "selcuk.m3u"
STATIC_LOGO_URL = "https://i.hizliresim.com/8xzjgqv.jpg"

SELCUK_NAMES = {
    "selcukbeinsports1": "Bein Sports 1",
    "selcukbeinsports2": "Bein Sports 2",
    "selcukbeinsports3": "Bein Sports 3",
    "selcukbeinsports4": "Bein Sports 4",
    "selcukbeinsports5": "Bein Sports 5",
    "selcukbeinsportshaber": "Bein Sports Haber",
    "selcukbeinsportsmax1": "Bein Sports Max 1",
    "selcukbeinsportsmax2": "Bein Sports Max 2",
    "selcukssport": "S Sport",
    "selcukssport2": "S Sport 2",
    "selcuksmartspor": "Smart Spor",
    "smartspor2": "Smart Spor 2",
    "selcuktivibuspor": "Tivibu Spor",
    "selcuktivibuspor1": "Tivibu Spor 1",
    "selcuktivibuspor2": "Tivibu Spor 2",
    "selcuktivibuspor3": "Tivibu Spor 3",
    "selcuktivibuspor4": "Tivibu Spor 4",
    "selcuktabiispor": "tabii Spor",
    "selcuktabiispor1": "tabii Spor 1",
    "selcuktabiispor2": "tabii Spor 2",
    "selcuktabiispor3": "tabii Spor 3",
    "tabiispor4": "tabii Spor 4",
    "tabiispor5": "tabii Spor 5",
    "selcuktabiispor6": "tabii Spor 6",
    "selcuktabiispor7": "tabii Spor 7",
    "ssplus1": "S Sport Plus 1",
    "selcukssplus2": "S Sport Plus 2",
    "selcukssplus3": "S Sport Plus 3",
    "selcukssplus4": "S Sport Plus 4",
    "selcukssplus5": "S Sport Plus 5",
    "selcukssplus6": "S Sport Plus 6",
    "selcukssplus7": "S Sport Plus 7",
    "selcukssplus8": "S Sport Plus 8",
    "selcukssplus9": "S Sport Plus 9",
    "selcukssplus10": "S Sport Plus 10",
    "selcukaspor": "A Spor",
    "selcuktrtspor": "TRT Spor",
    "trtspor2": "TRT Spor 2",
    "selcuktrtavaz": "TRT Avaz"
}

def get_html(url, use_proxy=False):
    """Fetches HTML directly or via proxy if needed"""
    target_url = PROXY_URL + url if use_proxy else url
    try:
        r = requests.get(target_url, headers=HEADERS, timeout=TIMEOUT_VAL, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching {target_url}: {e}")
        return None

def get_active_domain_from_github():
    """Fetches the current active domain from the GitHub raw file"""
    print("--- 📡 Fetching active domain from GitHub ---")
    text = get_html(GITHUB_DOMAIN_URL, use_proxy=False)
    if not text:
        return None
    
    for line in text.splitlines():
        if line.startswith("selcuk_guncel_domain="):
            domain = line.split("=", 1)[1].strip()
            if not domain.endswith('/'):
                domain += '/'
            return domain
    return None

def find_stream_details(active_domain):
    """Scans the main page and player pages to extract base stream URL and origin"""
    print(f"🔗 Connecting to active domain: {active_domain}")
    
    # Önce direkt bağlanmayı dene, başarısız olursa proxy kullan
    domain_html = get_html(active_domain, use_proxy=False)
    if not domain_html:
        print("⚠️ Direct connection failed, trying via proxy...")
        domain_html = get_html(active_domain, use_proxy=True)
    
    if not domain_html:
        print("❌ Could not load active domain page.")
        return None, None

    # Find player links
    player_links = re.findall(r'data-url=["\'](https?://[^"\']+?id=[^"\']+?)["\']', domain_html)
    if not player_links:
        player_links = re.findall(r'href=["\'](https?://[^"\']+?index\.php\?id=[^"\']+?)["\']', domain_html)
    
    if not player_links:
        print("❌ No player links found.")
        return None, None

    base_stream_url = ""
    origin_url = ""

    patterns = [
        r'this\.baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]',
        r'const baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]',
        r'baseStreamUrl\s*:\s*[\'"](https://[^\'"]+)[\'"]',
        r'streamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]'
    ]

    origin_patterns = [
        r'origin\s*[:=]\s*[\'"](https://[^\'"]+)[\'"]',
        r'parent\s*[:=]\s*[\'"](https://[^\'"]+)[\'"]'
    ]

    for player_url in player_links:
        html_player = get_html(player_url, use_proxy=False)
        if html_player:
            for op in origin_patterns:
                om = re.search(op, html_player)
                if om:
                    origin_url = om.group(1)
                    break

            for pattern in patterns:
                stream_match = re.search(pattern, html_player)
                if stream_match:
                    base_stream_url = stream_match.group(1)
                    if 'live/' in base_stream_url:
                        base_stream_url = base_stream_url.split('live/')[0] + 'live/'
                    break
            
            if base_stream_url:
                break

    if not base_stream_url:
        print("❌ Base stream URL not found.")
        return None, None

    if not base_stream_url.endswith('/'):
        base_stream_url += '/'
    if 'live/' not in base_stream_url:
        base_stream_url = base_stream_url.rstrip('/') + '/live/'

    if not origin_url:
        parsed = urllib.parse.urlparse(base_stream_url)
        origin_url = f"{parsed.scheme}://{parsed.netloc}"

    return base_stream_url, origin_url

def main():
    print("Starting playlist generator...")
    
    active_domain = get_active_domain_from_github()
    if not active_domain:
        print("⚠️ Could not retrieve active domain from GitHub.")
        return
    
    print(f"✅ Active Domain Found: {active_domain}")

    base_url, origin_url = find_stream_details(active_domain)
    if not base_url:
        print("⚠️ Process aborted due to missing stream details.")
        return

    print(f"🎯 Base Stream URL: {base_url}")
    print(f"🌐 Origin URL: {origin_url}")

    m3u_lines = ["#EXTM3U"]
    
    print(f"⚡ Generating playlist entries...")

    for selcuk_id, display_name in SELCUK_NAMES.items():
        stream_url = f"{base_url}{selcuk_id}/playlist.m3u8"
        
        entry = (
            f'#EXTINF:-1 tvg-name="{display_name}" tvg-logo="{STATIC_LOGO_URL}" group-title="Selçuk TV",{display_name}\n'
            f'#EXT-X-USER-AGENT:{USER_AGENT}\n'
            f'#EXT-X-REFERER:{active_domain}\n'
            f'#EXT-X-ORIGIN:{origin_url}\n'
            f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
            f'#EXTVLCOPT:http-referrer={active_domain}\n'
            f'#EXTVLCOPT:http-origin={origin_url}\n'
            f'{stream_url}'
        )
        m3u_lines.append(entry)

    trt1_entry = (
        f'#EXTINF:-1 tvg-name="TRT 1" tvg-logo="{STATIC_LOGO_URL}" group-title="Selçuk TV",TRT 1\n'
        f'https://tv-trt1.medya.trt.com.tr/master.m3u8'
    )
    m3u_lines.append(trt1_entry)

    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        
        full_path = os.path.abspath(OUTPUT_FILENAME)
        print(f"\n✅ SUCCESS: Playlist created successfully!")
        print(f"💾 File: {OUTPUT_FILENAME}")
        print(f"📝 Total Channels: {len(SELCUK_NAMES) + 1}")
        print(f"📍 Path: {full_path}")

    except IOError as e:
        print(f"\n❌ File write error: {e}")

if __name__ == "__main__":
    main()
