from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_CODE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube İndirici</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white min-h-screen flex items-center justify-center p-4">
  <div class="w-full max-w-xl bg-gray-900 rounded-2xl shadow-2xl p-8 border border-gray-800 text-center">
    <h1 class="text-3xl font-bold mb-2 text-red-500">YouTube İndirici</h1>
    <p class="text-gray-400 mb-8">Linki yapıştır ve SaveFrom.net\'e git</p>

    <input 
      type="text" 
      id="link" 
      placeholder="https://youtube.com/watch?v=..."
      class="w-full px-5 py-4 bg-gray-800 border border-gray-700 rounded-xl mb-4 focus:outline-none focus:border-red-500 text-lg text-center">
    
    <button onclick="yönlendir()" class="w-full bg-green-600 hover:bg-green-700 py-4 rounded-xl font-bold text-xl transition mb-4">
      SaveFrom.net'de Aç
    </button>
    
    <p class="text-gray-500 text-sm mt-4">Butona basınca otomatik yönlendirileceksiniz</p>
  </div>

  <script>
    function yönlendir() {
      const link = document.getElementById("link").value.trim();
      
      if(!link.includes("youtube") && !link.includes("youtu.be")) {
        alert("Geçerli YouTube linki girin!");
        return;
      }
      
      // SaveFrom.net'e yönlendir
      const hedef = "https://savefrom.net/?url=" + encodeURIComponent(link);
      window.open(hedef, '_blank');
    }
  </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
