from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url or ('youtube' not in url and 'youtu.be' not in url):
        return jsonify({'error': 'Geçerli YouTube URLsi girin'}), 400

    try:
        # Step 1: Video bilgilerini al
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        search_data = {'q': url, 'vt': 'home'}
        r = requests.post('https://yt1s.com/api/ajaxSearch/index', 
                         data=search_data, headers=headers, timeout=10)
        
        result = r.json()
        
        if result.get('status') != 'ok':
            return jsonify({'error': 'Video bulunamadı veya bu video özel/kısıtlı'}), 400
        
        # Kaliteleri hazırla
        formats = []
        
        # MP4ler
        if 'mp4' in result.get('links', {}):
            for key, item in result['links']['mp4'].items():
                formats.append({
                    'quality': item['q'],
                    'size': item.get('size', 'Bilinmiyor'),
                    'vid': result['vid'],
                    'key': item['k'],
                    'type': 'video'
                })
        
        # MP3ler
        if 'mp3' in result.get('links', {}):
            for key, item in result['links']['mp3'].items():
                formats.append({
                    'quality': 'Ses (MP3)',
                    'size': item.get('size', 'Bilinmiyor'),
                    'vid': result['vid'],
                    'key': item['k'],
                    'type': 'audio'
                })

        return jsonify({
            'title': result.get('title', 'Video'),
            'formats': formats
        })

    except Exception as e:
        return jsonify({'error': f'API Hatası: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    vid = data.get('vid')
    key = data.get('key')
    
    if not vid or not key:
        return jsonify({'error': 'Eksik parametre'}), 400
    
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        convert_data = {'vid': vid, 'k': key}
        r = requests.post('https://yt1s.com/api/ajaxConvert/convert',
                         data=convert_data, headers=headers, timeout=10)
        
        result = r.json()
        
        if result.get('dlink'):
            return jsonify({'url': result['dlink']})
        else:
            return jsonify({'error': 'İndirme linki oluşturulamadı'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
