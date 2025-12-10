from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests
import logging

# Logları temizle
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
# Tüm sitelerden gelen isteklere izin ver (CORS Bypass)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "<h1>ERENBABA LISTENER AKTIF</h1>", 200

# --- ADMIN SCANNER ENDPOINT ---
@app.route('/scan', methods=['GET'])
def scan():
    target_url = request.args.get('url')
    if not target_url: return jsonify({'status': 0}), 400

    try:
        # Chrome 120 taklidi yaparak Cloudflare'i delip geçiyoruz
        response = cffi_requests.get(
            target_url,
            impersonate="chrome120",
            timeout=8,
            allow_redirects=True
        )
        return jsonify({
            'status': response.status_code, 
            'url': response.url,
            'success': True
        })
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e), 'success': False})

# --- SMS BOMBER ENDPOINT (Gerekirse) ---
# ... (SMS kodlarını buraya ekleyebilirsin)

if __name__ == '__main__':
    # Render için port ayarı
    app.run(host='0.0.0.0', port=10000)
