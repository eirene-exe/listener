import time
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from curl_cffi import requests as cffi_requests

app = Flask(__name__)
CORS(app)  # Cross-Origin hatalarını engelle

# --- GÜVENLİK DUVARI BYPASS AYARLARI ---
# Bu User-Agent ve Impersonate ayarları sayesinde
# Cloudflare ve benzeri korumalar isteği gerçek bir insan sanar.
BROWSER_PROFILES = [
    "chrome120",
    "chrome119",
    "safari17_2",
    "edge101"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
]

@app.route('/')
def index():
    # Frontend arayüzünü yükler
    return render_template('index.html')

@app.route('/check_path', methods=['POST'])
def check_path():
    """
    Frontend'den gelen URL'i kontrol eder.
    Gerçek bir tarayıcı taklidi yapar.
    """
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL girilmedi'}), 400

    # Rastgele bir tarayıcı kimliği seç
    profile = random.choice(BROWSER_PROFILES)
    user_agent = random.choice(USER_AGENTS)

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://google.com'
    }

    try:
        # --- KRİTİK NOKTA: REQUEST ---
        # impersonate parametresi TLS parmak izini değiştirir.
        # Bu sayede WAF'lar (Web Application Firewall) bizi script olarak algılayamaz.
        response = cffi_requests.get(
            target_url,
            impersonate=profile,
            headers=headers,
            timeout=8,
            allow_redirects=True
        )

        status_code = response.status_code
        
        # Sonuç analizi
        result = {
            "url": target_url,
            "status": status_code,
            "found": False
        }

        # 200 (Açık), 403 (Yasaklı ama var), 401 (Şifreli ama var), 302 (Yönlendirme)
        if status_code in [200, 301, 302, 401, 403]:
            result["found"] = True
        
        return jsonify(result)

    except Exception as e:
        # Bağlantı hatası olsa bile script durmasın
        return jsonify({
            "url": target_url,
            "status": 0,
            "error": str(e),
            "found": False
        })

if __name__ == '__main__':
    print("🚀 ErenBaba Admin Finder Başlatıldı...")
    print("🌍 Server: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
