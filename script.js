async function analyze() {
  const url = document.getElementById("url").value.trim();
  const result = document.getElementById("result");

  if (!url) return alert("Link gir kral!");

  result.innerHTML = `<p style="text-align:center;color:#c4b5fd;padding:50px 0;">Analiz ediliyor...</p>`;

  try {
    const res = await fetch('/api/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    const data = await res.json();

    if (data.success) {
      result.innerHTML = `
        <div class="result-card">
          ${data.thumbnail ? `<img src="${data.thumbnail}">` : ''}
          <p style="margin:15px 0 20px 0; font-weight:600;">${data.title}</p>
          <a href="${data.download_url}" target="_blank" class="download-btn">
            İNDİR
          </a>
        </div>`;
    } else {
      result.innerHTML = `<p style="color:#fda4af;text-align:center;padding:30px;">${data.error || 'Bu platform şu an çalışmıyor'}</p>`;
    }
  } catch (e) {
    result.innerHTML = `<p style="color:#fda4af;text-align:center;padding:30px;">Bağlantı hatası</p>`;
  }
}
