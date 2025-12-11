from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

# WAF Kandırma Headerları
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

@app.route('/')
def home(): return jsonify({"status": "Online"})

@app.route('/scan', methods=['GET'])
def scan():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400

    try:
        # Rastgele Bekleme (Daha kısa tuttum seri olması için)
        time.sleep(random.uniform(0.5, 1.5))

        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': 'https://www.google.com/'
        }
        
        # İstek At
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
        content = response.text.lower()
        status = response.status_code

        # --- CLOUDFLARE KONTROLÜ ---
        # Cloudflare genellikle 503 döndürür ve "just a moment" yazar
        cf_detected = False
        if status == 503 and ("just a moment" in content or "cloudflare" in content):
            cf_detected = True

        return jsonify({
            "url": url,
            "status": status,
            "cf_detected": cf_detected, # Yeni özellik
            "found": status in [200, 403, 301, 302]
        })

    except Exception as e:
        return jsonify({"url": url, "status": 0, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
