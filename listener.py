from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests
import random
import datetime # Tarih için eklendi

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- YENİ EKLENEN KISIM: LOGLARI TUTACAK HAFIZA ---
LOGS = []
LOG_ID = 1
# --------------------------------------------------

BROWSER_PROFILES = [
    "chrome120", "chrome119", "safari17_2", "edge101"
]

@app.route('/')
def home():
    return "<h1>ERENBABA HUNTER AKTIF (Loglu Versiyon)</h1>", 200

# --- YENİ EKLENEN KISIM: ADMIN PANELİ İÇİN LOGLARI VERİR ---
@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(LOGS)
# -----------------------------------------------------------

@app.route('/scan', methods=['GET'])
def scan():
    global LOG_ID
    target_url = request.args.get('url')

    if not target_url:
        return jsonify({'status': 0, 'error': 'URL yok'}), 400

    try:
        browser_id = random.choice(BROWSER_PROFILES)
        
        response = cffi_requests.get(
            target_url,
            impersonate=browser_id,
            timeout=10,
            allow_redirects=True
        )

        # --- YENİ EKLENEN KISIM: SONUCU KAYDET ---
        # Sadece bulunanları (200) veya yasaklıları (403) admin paneline kaydet
        if response.status_code in [200, 403]:
            log_entry = {
                "id": LOG_ID,
                "url": target_url,
                "status": response.status_code,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            }
            LOGS.append(log_entry)
            LOG_ID += 1
            
            # Hafıza şişmesin diye son 100 logu tutalım
            if len(LOGS) > 100:
                LOGS.pop(0)
        # ----------------------------------------

        return jsonify({
            'status': response.status_code,
            'url': response.url,
            'success': True
        })

    except Exception as e:
        return jsonify({'status': 0, 'error': str(e), 'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
