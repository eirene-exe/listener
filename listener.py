from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests
import random

app = Flask(__name__)

# Tüm güvenlik kısıtlamalarını kaldır (Frontend rahat bağlansın)
CORS(app, resources={r"/*": {"origins": "*"}})

# Farklı tarayıcı kimlikleri (Her istekte bunlardan biri seçilecek)
BROWSER_PROFILES = [
    "chrome120",
    "chrome119", 
    "safari17_2",
    "edge101"
]

@app.route('/')
def home():
    return "<h1>ERENBABA HUNTER AKTIF (Render)</h1>", 200

@app.route('/scan', methods=['GET'])
def scan():
    target_url = request.args.get('url')

    if not target_url:
        return jsonify({'status': 0, 'error': 'URL yok'}), 400

    try:
        # Rastgele bir tarayıcı seç (Sürekli aynı kişi gibi görünmemek için)
        browser_id = random.choice(BROWSER_PROFILES)
        
        print(f"Tarama yapılıyor: {target_url} | Kimlik: {browser_id}")

        # --- KRİTİK NOKTA ---
        # curl_cffi kütüphanesi burada devreye giriyor.
        # TLS parmak izini (JA3) değiştirerek Cloudflare'i kandırmaya çalışır.
        
        response = cffi_requests.get(
            target_url,
            impersonate=browser_id, # Tarayıcıyı taklit et
            timeout=10,             # Zaman aşımını biraz artırdım (Render yavaş olabilir)
            allow_redirects=True
        )

        return jsonify({
            'status': response.status_code,
            'url': response.url,
            'success': True
        })

    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
        # Hata olsa bile script çökmesin, JSON dönsün
        return jsonify({'status': 0, 'error': str(e), 'success': False})

if __name__ == '__main__':
    # Render genelde PORT çevresel değişkenini kullanır ama 
    # Dockerfile kullanmıyorsan 8080 veya 10000 sık kullanılır.
    # Bu kod doğrudan çalıştırıldığında 8080'den yayın yapar.
    app.run(host='0.0.0.0', port=8080)
