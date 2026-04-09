from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

def get_video_id(url):
    # YouTube URL'sinden ID çıkar
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return None

@app.route('/')
def home():
    return render_template_string(open('index.html').read())

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    video_id = get_video_id(url)
    if not video_id:
        return jsonify({'error': 'Geçersiz URL'}), 400

    try:
        # Piped API - YouTube'un alternatifi, Render'dan erişilebilir
        api_url = f"https://pipedapi.moomoo.me/streams/{video_id}"
        response = requests.get(api_url, timeout=10)
        data = response.json()

        if 'error' in data:
            return jsonify({'error': 'Video bulunamadı veya özel'}), 404

        # Video kalitelerini ayıkla
        formats = []
        
        # Video + Ses birleşik (MP4)
        for stream in data.get('videoStreams', []):
            if stream.get('url') and stream.get('quality'):
                formats.append({
                    'quality': stream['quality'].replace('p', '') + 'p',
                    'url': stream['url'],
                    'type': 'video'
                })

        # Sadece Ses (MP3/Audio)
        for stream in data.get('audioStreams', []):
            if stream.get('url'):
                formats.append({
                    'quality': 'Ses (MP3)',
                    'url': stream['url'],
                    'type': 'audio'
                })

        return jsonify({
            'title': data.get('title', 'Video'),
            'thumbnail': data.get('thumbnailUrl', ''),
            'uploader': data.get('uploader', 'Bilinmiyor'),
            'formats': formats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
