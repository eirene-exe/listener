from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

found_panels = []

# --- 1. GİZLİLİK ARAÇLARI ---
# WAF'ı kandırmak için farklı tarayıcı kimlikleri
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

@app.route('/')
def home():
    return jsonify({"msg": "Erenbaba Stealth Scanner ONLINE", "mode": "WAF_BYPASS"})

@app.route('/ping')
def ping():
    return jsonify({"status": "pong"})

@app.route('/scan', methods=['GET'])
def scan():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400

    try:
        # --- 2. TIMEOUTLU BYPASS MANTIĞI ---
        # Seri istek atıp yakalanmamak için 1 ile 3 saniye arası rastgele bekle
        # Bu, senin dediğin o "eski yöntem"dir.
        sleep_time = random.uniform(1.0, 3.0) 
        time.sleep(sleep_time)

        # Rastgele bir tarayıcı seç
        current_ua = random.choice(USER_AGENTS)

        # Headerları güçlendir (Google'dan gelmiş gibi yap)
        headers = {
            'User-Agent': current_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/', # Google'dan gelmiş gibi göster
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        # Timeout süresini kısalttık (5sn), cevap vermeyen siteye takılmasın
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        
        status = response.status_code
        
        # LOGLAMA MANTIĞI:
        # 200: Kesin bulundu (Admin paneli açık)
        # 301/302: Yönlendirme (Genelde /login'e atar, bu da bulunduğunu gösterir)
        # 403: Eğer WAF hepsine 403 vermiyorsa, tekil 403 "Burası var ama giremezsin" demektir.
        
        is_found = False
        
        # Eğer sayfa içeriğinde login formu varsa ve status 200 ise kesin bulduk
        page_content = response.text.lower()
        has_login_form = "password" in page_content or "type=\"password\"" in page_content
        
        if status == 200 and has_login_form:
            is_found = True
        elif status in [301, 302]: # Yönlendirmeler genelde login panelidir
            is_found = True
        elif status == 403 and "cloudflare" not in page_content: 
            # Cloudflare engeli değilse, gerçek 403 olabilir
            is_found = True

        if is_found:
            log_entry = {
                "id": len(found_panels) + 1,
                "url": url,
                "status": status,
                "timestamp": time.strftime("%H:%M:%S")
            }
            if not any(p['url'] == url for p in found_panels):
                found_panels.append(log_entry)

        return jsonify({
            "url": url,
            "status": status,
            "found": is_found
        })

    except Exception as e:
        return jsonify({"url": url, "status": 0, "error": str(e)})

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(found_panels)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
