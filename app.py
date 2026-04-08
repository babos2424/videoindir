from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Frontend'in sorunsuz bağlanması için

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL gerekli'}), 400

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            # Sadece MP4 videoları al (720p, 1080p vb.)
            for f in info['formats']:
                if f.get('ext') == 'mp4' and f.get('height') and f.get('url'):
                    formats.append({
                        'format_id': f['format_id'],
                        'quality': f"{f['height']}p",
                        'url': f['url']  # Doğrudan indirme linki
                    })
            
            return jsonify({
                'title': info['title'],
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
