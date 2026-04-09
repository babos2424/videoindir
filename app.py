from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def detect_platform(url):
    url_lower = url.lower().strip()
    if 'instagram.com' in url_lower or 'instagr.am' in url_lower:
        return 'instagram'
    elif 'tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower or 'vt.tiktok.com' in url_lower:
        return 'tiktok'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower or 'fb.com' in url_lower:
        return 'facebook'
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL boş olamaz'}), 400
    
    platform = detect_platform(url)
    if not platform:
        return jsonify({'error': f'Desteklenmeyen URL formatı: {url[:50]}... Sadece Instagram, TikTok ve Facebook desteklenir'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'cookiesfrombrowser': None,  # Tarayıcı cookiesi kullanma
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            
            # Video formatları (ses+video birlikte)
            if 'formats' in info:
                video_formats = [f for f in info['formats'] 
                               if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url')]
                
                # Kaliteye göre sırala (en yüksekten düşüğe)
                video_formats.sort(key=lambda x: (x.get('height', 0) or 0), reverse=True)
                
                # En iyi 5 formatı al
                for f in video_formats[:5]:
                    height = f.get('height', 0)
                    quality = f"{height}p" if height else 'HD'
                    formats.append({
                        'url': f['url'],
                        'quality': quality,
                        'type': 'video',
                        'ext': f.get('ext', 'mp4')
                    })
            
            # En iyi ses formatı
            if 'formats' in info:
                audio_formats = [f for f in info['formats'] 
                               if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')]
                if audio_formats:
                    best_audio = max(audio_formats, key=lambda x: (x.get('abr', 0) or 0))
                    formats.append({
                        'url': best_audio['url'],
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
                'formats': formats[:6]  # En fazla 6 seçenek
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"HATA DETAYI: {error_msg}")  # Render logs'a yazılır
        if "Sign in" in error_msg or "confirm" in error_msg or "robot" in error_msg:
            return jsonify({'error': f'{platform.capitalize()} bu IP\'yi bot olarak algıladı. Farklı bir link deneyin.'}), 500
        return jsonify({'error': f'Video işlenirken hata: {error_msg[:100]}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
