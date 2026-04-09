from flask import Flask, render_template, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

def detect_platform(url):
    url = url.lower().strip()
    patterns = {
        'instagram': r'(instagram\.com|instagr\.am)',
        'tiktok': r'(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|m\.tiktok\.com)',
        'facebook': r'(facebook\.com|fb\.watch|fb\.com)'
    }
    
    for platform, pattern in patterns.items():
        if re.search(pattern, url):
            return platform
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Link boş olamaz'}), 400
    
    platform = detect_platform(url)
    if not platform:
        return jsonify({'error': 'Desteklenmeyen link. Sadece Instagram, TikTok ve Facebook çalışır.'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            
            # Video+Ses birlikte (kaliteli)
            video_formats = [f for f in info.get('formats', []) 
                           if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height')]
            
            video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
            
            for f in video_formats[:3]:  # En iyi 3 kalite
                formats.append({
                    'url': f['url'],
                    'quality': f"{f['height']}p" if f.get('height') else 'HD',
                    'type': 'video',
                    'ext': f.get('ext', 'mp4'),
                    'size': f"{f.get('filesize', 0)//1024//1024}MB" if f.get('filesize') else ''
                })
            
            # Ses only
            audio_formats = [f for f in info.get('formats', []) 
                           if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                formats.append({
                    'url': best_audio['url'],
                    'quality': 'Sadece Ses (MP3)',
                    'type': 'audio',
                    'ext': 'mp3',
                    'size': ''
                })

            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'platform': platform,
                'uploader': info.get('uploader', info.get('channel', 'Bilinmiyor')),
                'duration': info.get('duration_string', ''),
                'formats': formats
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"HATA: {error_msg}")
        if "robot" in error_msg.lower() or "confirm" in error_msg.lower():
            return jsonify({'error': f'{platform.capitalize()} geçici olarak erişimi kısıtladı. Birkaç dakika sonra tekrar dene.'}), 500
        return jsonify({'error': 'Video bilgileri alınamadı. Linki kontrol et.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
