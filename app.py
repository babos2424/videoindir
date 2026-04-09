from flask import Flask, render_template_string, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

# HTML CSS JS - Hepsi burada
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VidFetch Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 40px;
            width: 100%;
            max-width: 600px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.95rem;
        }
        .input-group {
            position: relative;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            font-size: 16px;
            transition: all 0.3s;
            outline: none;
        }
        input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-weight: 600;
        }
        .error {
            display: none;
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            text-align: center;
        }
        .result {
            display: none;
            margin-top: 25px;
            animation: slideUp 0.4s ease;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .video-info {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        .video-info img {
            width: 120px;
            height: 90px;
            object-fit: cover;
            border-radius: 10px;
        }
        .video-meta h3 {
            font-size: 16px;
            color: #333;
            margin-bottom: 5px;
            line-height: 1.4;
        }
        .video-meta p {
            font-size: 13px;
            color: #666;
        }
        .download-btn {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 10px;
            text-decoration: none;
            color: #333;
            transition: all 0.2s;
        }
        .download-btn:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .download-btn .quality {
            font-weight: bold;
            color: #667eea;
        }
        .download-btn .action {
            background: #667eea;
            color: white;
            padding: 6px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
        }
        .platform-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .ig { background: #E1306C; color: white; }
        .tt { background: #000; color: white; }
        .fb { background: #1877F2; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VidFetch Pro</h1>
        <p class="subtitle">Instagram • TikTok • Facebook</p>
        
        <div class="input-group">
            <input type="text" id="urlInput" placeholder="Video linkini yapıştır...">
        </div>
        
        <button onclick="fetchVideo()" id="downloadBtn">
            Videoyu İndir
        </button>
        
        <div class="loading" id="loading">İşleniyor...</div>
        <div class="error" id="error"></div>
        
        <div class="result" id="result">
            <div class="video-info" id="videoInfo"></div>
            <div id="downloadLinks"></div>
        </div>
    </div>

    <script>
        async function fetchVideo() {
            const url = document.getElementById('urlInput').value.trim();
            const btn = document.getElementById('downloadBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const result = document.getElementById('result');
            
            if(!url) {
                showError('Lütfen bir link yapıştırın');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'İşleniyor...';
            loading.style.display = 'block';
            error.style.display = 'none';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/api/info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                const data = await response.json();
                
                if(!response.ok) throw new Error(data.error || 'Hata oluştu');
                
                // Platform badge
                let badgeClass = '';
                let badgeText = '';
                if(data.platform === 'instagram') { badgeClass = 'ig'; badgeText = 'Instagram'; }
                else if(data.platform === 'tiktok') { badgeClass = 'tt'; badgeText = 'TikTok'; }
                else { badgeClass = 'fb'; badgeText = 'Facebook'; }
                
                document.getElementById('videoInfo').innerHTML = `
                    <img src="${data.thumbnail}" onerror="this.style.display='none'">
                    <div class="video-meta">
                        <span class="platform-badge ${badgeClass}">${badgeText}</span>
                        <h3>${data.title}</h3>
                        <p>${data.uploader}</p>
                        ${data.duration ? `<p>⏱ ${data.duration}</p>` : ''}
                    </div>
                `;
                
                let linksHtml = '';
                data.formats.forEach(f => {
                    const isAudio = f.type === 'audio';
                    linksHtml += `
                        <a href="${f.url}" target="_blank" class="download-btn">
                            <span class="quality">${f.quality} ${f.size || ''}</span>
                            <span class="action">${isAudio ? 'Ses İndir' : 'Video İndir'}</span>
                        </a>
                    `;
                });
                
                document.getElementById('downloadLinks').innerHTML = linksHtml;
                result.style.display = 'block';
                
            } catch(e) {
                showError(e.message);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Videoyu İndir';
                loading.style.display = 'none';
            }
        }
        
        function showError(msg) {
            document.getElementById('error').textContent = msg;
            document.getElementById('error').style.display = 'block';
        }
        
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if(e.key === 'Enter') fetchVideo();
        });
    </script>
</body>
</html>
'''

def detect_platform(url):
    url = url.lower().strip()
    if 'instagram' in url: return 'instagram'
    if 'tiktok' in url: return 'tiktok'
    if 'facebook' in url or 'fb.watch' in url: return 'facebook'
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Link boş'}), 400
    
    platform = detect_platform(url)
    if not platform:
        return jsonify({'error': 'Sadece Instagram, TikTok, Facebook desteklenir'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            
            # Video+Ses
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height'):
                    formats.append({
                        'url': f['url'],
                        'quality': f"{f['height']}p",
                        'type': 'video',
                        'size': ''
                    })
            
            formats.sort(key=lambda x: int(x['quality'][:-1]), reverse=True)
            formats = formats[:3]  # En iyi 3
            
            # Ses
            audio_formats = [f for f in info.get('formats', []) 
                           if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                formats.append({
                    'url': best_audio['url'],
                    'quality': 'MP3 Ses',
                    'type': 'audio',
                    'size': ''
                })

            return jsonify({
                'title': info.get('title', 'Video')[:60],
                'thumbnail': info.get('thumbnail', ''),
                'platform': platform,
                'uploader': info.get('uploader', 'Bilinmiyor')[:30],
                'duration': info.get('duration_string', ''),
                'formats': formats
            })
            
    except Exception as e:
        print(f"HATA: {e}")
        return jsonify({'error': 'Video bilgisi alınamadı. Linki kontrol et.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
