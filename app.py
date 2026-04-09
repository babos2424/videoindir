from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Link eksik'}), 400

    try:
        # TikTok linklerini temizle
        if 'tiktok.com' in url and '@' in url:
            # TikTok kısa link formatına çevirmeye çalış
            url = url.split('?')[0]

        payload = {
            "url": url,
            "isAudioOnly": False,
            "isNoTTWatermark": True,
            "filenameStyle": "classic"
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.post("https://api.cobalt.tools/api/json", 
                               json=payload, 
                               headers=headers, 
                               timeout=15)

        print(f"API Status: {response.status_code}")  # Log için

        if response.status_code == 400:
            return jsonify({'error': 'Bu TikTok linki desteklenmiyor. Farklı bir TikTok linki deneyin (örneğin paylaş butonundan kopyalanmış link).'}), 400

        if response.status_code != 200:
            return jsonify({'error': f'API Hatası: {response.status_code}'}), response.status_code

        data = response.json()

        if data.get('url'):
            return jsonify({
                "success": True,
                "title": data.get("title", "Video"),
                "thumbnail": data.get("thumbnail"),
                "download_url": data.get("url")
            })
        else:
            return jsonify({'error': 'Video işlenemedi. Farklı bir link deneyin.'}), 400

    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
