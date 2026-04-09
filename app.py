from flask import Flask, Response, request, jsonify, render_template_string
import yt_dlp
import requests

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok İndirici Pro</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 50px 40px;
            width: 100%;
            max-width: 550px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.3);
            transform: translateY(0);
            animation: slideUp 0.6s ease;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo i {
            font-size: 60px;
            background: linear-gradient(45deg, #000000, #444444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            display: block;
        }
        
        h1 {
            text-align: center;
            color: #1a1a1a;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 5px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 15px;
            margin-bottom: 40px;
            font-weight: 500;
        }
        
        .input-wrapper {
            position: relative;
            margin-bottom: 25px;
        }
        
        input {
            width: 100%;
            padding: 18px 20px;
            border: 2px solid #e1e1e1;
            border-radius: 15px;
            font-size: 16px;
            transition: all 0.3s;
            background: #f8f9fa;
            outline: none;
        }
        
        input:focus {
            border-color: #fe2c55;
            background: white;
            box-shadow: 0 0 0 4px rgba(254, 44, 85, 0.1);
        }
        
        .btn-primary {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #fe2c55 0%, #ff0050 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(254, 44, 85, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(254, 44, 85, 0.5);
        }
        
        .btn-primary:active {
            transform: translateY(0);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
            color: #fe2c55;
            font-weight: 600;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #fe2c55;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .error {
            display: none;
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 12px;
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
            border-left: 4px solid #c33;
        }
        
        .result {
            display: none;
            margin-top: 30px;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        .video-card {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
        
        .video-thumb {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .video-title {
            font-weight: 700;
            color: #1a1a1a;
            font-size: 16px;
            line-height: 1.4;
            margin-bottom: 5px;
        }
        
        .video-author {
            color: #666;
            font-size: 14px;
        }
        
        .download-grid {
            display: grid;
            gap: 12px;
        }
        
        .download-btn {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            text-decoration: none;
            color: #1a1a1a;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .download-btn:hover {
            border-color: #fe2c55;
            background: #fff5f7;
            transform: translateX(5px);
        }
        
        .file-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .file-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #fe2c55 0%, #ff0050 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .file-name {
            font-weight: 700;
            font-size: 15px;
        }
        
        .file-desc {
            font-size: 13px;
            color: #666;
        }
        
        .download-action {
            background: #fe2c55;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 14px;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <i class="fab fa-tiktok"></i>
            <h1>TikTok İndirici</h1>
            <div class="subtitle">Filigransız video ve ses indir</div>
        </div>
        
        <div class="input-wrapper">
            <input type="text" id="urlInput" placeholder="TikTok linkini yapıştır (örn: vm.tiktok.com/...)">
        </div>
        
        <button class="btn-primary" onclick="fetchVideo()" id="mainBtn">
            <i class="fas fa-download"></i> Videoyu Getir
        </button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            Video bilgileri alınıyor...
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="result" id="result">
            <div class="video-card" id="videoInfo"></div>
            <div class="download-grid" id="downloadLinks"></div>
        </div>
    </div>

    <script>
        async function fetchVideo() {
            const url = document.getElementById('urlInput').value.trim();
            const btn = document.getElementById('mainBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const result = document.getElementById('result');
            
            if(!url) {
                alert('Lütfen bir TikTok linki yapıştırın');
                return;
            }
            
            if(!url.includes('tiktok')) {
                alert('Sadece TikTok linkleri desteklenir!');
                return;
            }
            
            btn.style.display = 'none';
            loading.style.display = 'block';
            error.style.display = 'none';
            result.style.display = 'none';
            
            try {
                const res = await fetch('/api/get', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                
                const data = await res.json();
                
                if(!res.ok) throw new Error(data.error || 'Bir hata oluştu');
                
                // Video bilgilerini göster
                document.getElementById('videoInfo').innerHTML = `
                    <img src="${data.thumbnail}" class="video-thumb" onerror="this.style.display='none'">
                    <div class="video-title">${data.title}</div>
                    <div class="video-author"><i class="fas fa-user"></i> ${data.author}</div>
                `;
                
                // İndirme butonları
                const linksHtml = [];
                
                if(data.video_url) {
                    linksHtml.push(`
                        <div class="download-btn" onclick="window.location.href='/download?url=${encodeURIComponent(data.video_url)}&filename=tiktok_video.mp4&type=video'">
                            <div class="file-info">
                                <div class="file-icon"><i class="fas fa-video"></i></div>
                                <div>
                                    <div class="file-name">Video İndir</div>
                                    <div class="file-desc">MP4 • HD Kalite</div>
                                </div>
                            </div>
                            <div class="download-action"><i class="fas fa-arrow-down"></i> İndir</div>
                        </div>
                    `);
                }
                
                if(data.audio_url) {
                    linksHtml.push(`
                        <div class="download-btn" onclick="window.location.href='/download?url=${encodeURIComponent(data.audio_url)}&filename=tiktok_audio.mp3&type=audio'">
                            <div class="file-info">
                                <div class="file-icon" style="background: #1877f2;"><i class="fas fa-music"></i></div>
                                <div>
                                    <div class="file-name">Ses İndir</div>
                                    <div class="file-desc">MP3 • Sadece Müzik</div>
                                </div>
                            </div>
                            <div class="download-action" style="background: #1877f2;"><i class="fas fa-arrow-down"></i> İndir</div>
                        </div>
                    `);
                }
                
                document.getElementById('downloadLinks').innerHTML = linksHtml.join('');
                result.style.display = 'block';
                
            } catch(e) {
                error.textContent = 'Hata: ' + e.message;
                error.style.display = 'block';
                btn.style.display = 'block';
            } finally {
                loading.style.display = 'none';
            }
        }
        
        // Enter tuşu desteği
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if(e.key === 'Enter') fetchVideo();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML

@app.route('/api/get', methods=['POST'])
def get_video():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if 'tiktok' not in url.lower():
        return jsonify({'error': 'Sadece TikTok desteklenir'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # En iyi video (sesli)
            best_video = None
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    if not best_video or (f.get('height', 0) > best_video.get('height', 0)):
                        best_video = f
            
            # En iyi ses
            best_audio = None
            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    if not best_audio or (f.get('abr', 0) or 0) > (best_audio.get('abr', 0) or 0):
                        best_audio = f
            
            return jsonify({
                'title': info.get('title', 'TikTok Videosu')[:100],
                'thumbnail': info.get('thumbnail', ''),
                'author': info.get('uploader', 'Bilinmiyor')[:50],
                'video_url': best_video['url'] if best_video else None,
                'audio_url': best_audio['url'] if best_audio else None
            })
            
    except Exception as e:
        print(f"HATA: {e}")
        return jsonify({'error': 'Video bilgisi alınamadı. Linki kontrol edin.'}), 500

@app.route('/download')
def download():
    video_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    if not video_url:
        return 'URL bulunamadı', 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Video dosyasını çek
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        r.raise_for_status()
        
        # Direkt indirme olarak sun
        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                'Content-Type': r.headers.get('content-type', 'video/mp4'),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': r.headers.get('content-length')
            }
        )
        
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return f'İndirme başarısız: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
