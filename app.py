from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Ana sayfa
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Video linkini al ve indirme linki döndür
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'Link eksik'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            title = info.get('title', 'video')

            return jsonify({
                'success': True,
                'download_url': direct_url,
                'title': title
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
