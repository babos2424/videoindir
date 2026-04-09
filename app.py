from flask import Flask, Response, request, jsonify
import yt_dlp
import requests

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>VidFetch Pro</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .box { background: white; padding: 40px; border-radius: 20px; width: 90%; max-width: 500px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        h1 { color: #333; text-align: center; margin-bottom: 10px; }
        .sub { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 10px; font-size: 16px; margin-bottom: 15px; box-sizing: border-box; }
        button { width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; }
        button:hover { background: #5568d3; }
        .loading { display: none; text-align: center; padding: 20px; color: #667eea; }
        .error { display: none; background: #fee; color: #c33; padding: 15px; border-radius: 10px; margin-top: 15px; text-align: center; }
        .result { display: none; margin-top: 20px; }
        .item { display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #f5f5f5; border-radius: 10px; margin-bottom: 10px; }
        .btn { background: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>VidFetch Pro</h1>
        <div class="sub">TikTok Video İndirici</div>
        <input type="text" id="url" placeholder="TikTok linkini yapıştır...">
        <button onclick="getVideo()">Videoyu İndir</button>
        <div class="loading" id="loading">İşleniyor...</div>
        <div class="error" id="error"></div>
        <div class="result" id="result"></div>
    </div>
    <script>
        async function getVideo() {
            const url = document.getElementById('url').value.trim();
            if(!url) return alert('Link girin');
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('result').style.display = 'none';
            
            try {
                const res = await fetch('/api/get', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await res.json();
                if(data.error) throw new Error(data.error);
                
                document.getElementById('result').innerHTML = `
                    <div style="margin-bottom: 15px; font-weight: bold; color: #333;">${data.title}</div>
                    <div class="item">
                        <span>Video (HD)</span>
                        <a href="/download?url=${encodeURIComponent(data.video_url)}&name=video.mp4" class="btn">İndir</a>
                    </div>
                    ${data.audio_url ? `<div class="item"><span>Ses (MP3)</span><a href="/download?url=${encodeURIComponent(data.audio_url)}&name=audio.mp3" class="btn">İndir</a></div>` : ''}
                `;
                document.getElementById('result').style.display = 'block';
            } catch(e) {
                document.getElementById('error').textContent = e.message;
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/api/get', methods=['POST'])
def get_video():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if 'tiktok' not in url.lower():
        return jsonify({'error': 'Sadece TikTok desteklenir'}), 400
    
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # En iyi video
            best_video = None
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    if not best_video or (f.get('height', 0) > best_video.get('height', 0)):
                        best_video = f
            
            # En iyi ses
            best_audio = None
            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    if not best_audio or (f.get('abr', 0) > best_audio.get('abr', 0)):
                        best_audio = f
            
            return jsonify({
                'title': info.get('title', 'Video'),
                'video_url': best_video['url'] if best_video else None,
                'audio_url': best_audio['url'] if best_audio else None
            })
    except Exception as e:
        return jsonify({'error': 'Video bilgisi alınamadı: ' + str(e)}), 500

@app.route('/download')
def download():
    video_url = request.args.get('url')
    name = request.args.get('name', 'video.mp4')
    
    if not video_url:
        return 'URL yok', 400
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(video_url, headers=headers, stream=True)
        
        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                'Content-Type': r.headers.get('content-type', 'video/mp4'),
                'Content-Disposition': f'attachment; filename="{name}"'
            }
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
