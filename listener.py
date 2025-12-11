from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)

# CORS ayarları: Her yerden gelen isteklere izin ver (Vercel için şart)
CORS(app)

# Bulunan admin panellerini burada tutacağız (RAM'de)
found_panels = []

# 1. Ana Sayfa (Sunucunun çalıştığını anlamak için)
@app.route('/')
def home():
    return jsonify({"message": "Erenbaba Admin Hunter Listener is ONLINE", "status": "running"})

# 2. Ping (Render sunucusunu uyanık tutmak için)
@app.route('/ping')
def ping():
    return jsonify({"status": "pong"})

# 3. Tarama Fonksiyonu (Esas İş)
@app.route('/scan', methods=['GET'])
def scan():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL parametresi gerekli"}), 400

    try:
        # Siteye gerçek bir kullanıcı gibi istek atalım
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Timeout 5 saniye (Çok bekletmesin)
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
        
        status_code = response.status_code
        
        # Eğer panel bulunduysa (200) veya yasaklıysa (403), loglara ekle
        if status_code in [200, 403]:
            log_entry = {
                "id": len(found_panels) + 1,
                "url": url,
                "status": status_code,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            # Aynı URL zaten yoksa ekle
            if not any(p['url'] == url for p in found_panels):
                found_panels.append(log_entry)

        return jsonify({
            "url": url,
            "status": status_code,
            "found": status_code in [200, 403]
        })

    except requests.exceptions.RequestException as e:
        # Siteye ulaşılamadıysa
        return jsonify({
            "url": url,
            "status": 0,
            "error": str(e)
        })

# 4. Logları Getir (Frontend tablosu için)
@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(found_panels)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
