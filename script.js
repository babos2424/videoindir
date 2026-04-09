// Tema Yönetimi
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
  body.classList.toggle('light');
  const isLight = body.classList.contains('light');
  themeToggle.innerHTML = isLight ? 
    '<i class="fas fa-sun"></i>' : 
    '<i class="fas fa-moon"></i>';
});

// Ana Fonksiyon
async function analyzeLink() {
  const url = document.getElementById('urlInput').value.trim();
  const result = document.getElementById('result');

  if (!url) {
    result.innerHTML = `<p style="color:#ff5555; text-align:center;">Lütfen bir link yapıştırın!</p>`;
    return;
  }

  result.innerHTML = `
    <div class="result-card">
      <p style="text-align:center; color:#a5b4fc;">Analiz ediliyor...</p>
    </div>`;

  try {
    const res = await fetch('https://api.cobalt.tools/api/json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });

    const data = await res.json();

    if (data.url) {
      result.innerHTML = `
        <div class="result-card">
          ${data.thumbnail ? `<img src="${data.thumbnail}" style="width:100%; border-radius:16px; margin-bottom:15px;">` : ''}
          <h3 style="margin:10px 0 15px 0; color:#fff;">${data.title || 'İndirme Hazır'}</h3>
          <a href="${data.url}" target="_blank" 
             style="display:block; background:linear-gradient(90deg,#00ff88,#00cc66); color:black; padding:16px; border-radius:16px; text-align:center; font-weight:bold; text-decoration:none;">
            İndir (En İyi Kalite)
          </a>
        </div>`;
    } else {
      result.innerHTML = `<p style="color:#ff5555; text-align:center;">Bu link şu anda desteklenmiyor.</p>`;
    }
  } catch (err) {
    result.innerHTML = `<p style="color:#ff5555; text-align:center;">Bağlantı hatası oluştu.</p>`;
  }
}
