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
        payload = {
            "url": url,
            "isAudioOnly": False,
            "isNoTTWatermark": True,
            "filenameStyle": "classic"
        }

        response = requests.post(
            "https://api.cobalt.tools/api/json",
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=12
        )

        if response.status_code != 200:
            return jsonify({'error': f'API Hatası: {response.status_code}'}), 400

        data = response.json()

        if data.get('url'):
            return jsonify({
                "success": True,
                "title": data.get("title", "Video"),
                "thumbnail": data.get("thumbnail"),
                "download_url": data.get("url")
            })
        else:
            return jsonify({'error': 'Bu link şu anda desteklenmiyor. Farklı bir link deneyin.'}), 400

    except Exception as e:
        return jsonify({'error': 'Sunucu hatası oluştu.'}), 500

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
