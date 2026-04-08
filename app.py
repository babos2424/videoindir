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
    data = request.get_json()
    url = data.get('url')
    
    if not url or 'youtube' not in url:
        return jsonify({'error': 'Geçerli YouTube URLsi girin'}), 400

    try:
        # Cobalt.tools API - YouTube bot korumasını aşıyor
        api_url = "https://api.cobalt.tools/api/json"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            'url': url,
            'isAudioOnly': False,
            'filenamePattern': 'classic'
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('status') == 'error':
            return jsonify({'error': result.get('text', 'Video işlenemedi')}), 400
        
        # Başarılı dönüş
        if result.get('url'):
            return jsonify({
                'title': result.get('filename', 'Video'),
                'formats': [{
                    'format_id': 'best',
                    'quality': 'HD',
                    'url': result.get('url')  # Doğrudan indirme linki
                }]
            })
        else:
            return jsonify({'error': 'İndirme linki alınamadı'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
