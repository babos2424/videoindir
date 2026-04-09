from flask import Flask, render_template, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

def detect_platform(url):
    if 'instagram.com' in url or 'instagr.am' in url:
        return 'instagram'
    elif 'tiktok.com' in url or 'vm.tiktok.com' in url:
        return 'tiktok'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL gerekli'}), 400
    
    platform = detect_platform(url)
    if not platform:
        return jsonify({'error': 'Sadece Instagram, TikTok ve Facebook desteklenir'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            
            # En iyi kalite
            if info.get('url'):
                formats.append({
                    'url': info['url'],
                    'quality': 'Orijinal Kalite',
                    'type': 'video',
                    'ext': info.get('ext', 'mp4')
                })
            
            # Tüm formatlar
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('ext') in ['mp4', 'webm'] and f.get('height') and f.get('url'):
                        formats.append({
                            'url': f['url'],
                            'quality': f"{f['height']}p",
                            'type': 'video',
                            'ext': f['ext']
                        })
            
            # Ses (varsa)
            if 'requested_formats' not in info and info.get('url'):
                 formats.append({
                    'url': info['url'],
                    'quality': 'Ses (MP3)',
                    'type': 'audio',
                    'ext': 'mp3'
                })
            
            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'platform': platform,
                'uploader': info.get('uploader', info.get('channel', 'Bilinmiyor')),
                'duration': info.get('duration_string', ''),
                'formats': formats[:6]
            })
            
    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "confirm" in error_msg:
            return jsonify({'error': 'Bu platform şu an erişimi kısıtlı. Başka bir link deneyin.'}), 500
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
