const BACKEND_URL = 'http://localhost:5000';

let userSettings = {
    format: 'mp4',
    quality: '720p',
    subtitles: false
};

function loadSettings() {
    const saved = localStorage.getItem('baixaryou_settings');
    if (saved) {
        const settings = JSON.parse(saved);
        userSettings = { ...userSettings, ...settings };
        document.getElementById('formatSelect').value = userSettings.format;
        document.getElementById('qualitySelect').value = userSettings.quality;
        document.getElementById('downloadSubtitles').checked = userSettings.subtitles;
    }
}

function saveSettings() {
    localStorage.setItem('baixaryou_settings', JSON.stringify(userSettings));
}

async function baixarVideo(url) {
    const progressDiv = document.getElementById('downloadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressTitle = document.getElementById('progressTitle');
    
    progressDiv.style.display = 'block';
    progressTitle.textContent = 'Conectando...';
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                quality: userSettings.quality
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro no download');
        }
        
        progressTitle.textContent = 'Baixando...';
        progressFill.style.width = '70%';
        progressPercent.textContent = '70%';
        
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = 'video.mp4';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);
        
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        progressTitle.textContent = 'Concluído!';
        
        setTimeout(() => {
            progressDiv.style.display = 'none';
        }, 2000);
        
    } catch (error) {
        progressDiv.style.display = 'none';
        alert('❌ Erro: ' + error.message);
    }
}

document.getElementById('downloadBtn')?.addEventListener('click', () => {
    const url = document.getElementById('urlInput').value.trim();
    if (url) {
        baixarVideo(url);
    } else {
        alert('Cole uma URL válida');
    }
});

document.getElementById('formatSelect')?.addEventListener('change', (e) => {
    userSettings.format = e.target.value;
    saveSettings();
});

document.getElementById('qualitySelect')?.addEventListener('change', (e) => {
    userSettings.quality = e.target.value;
    saveSettings();
});

document.getElementById('downloadSubtitles')?.addEventListener('change', (e) => {
    userSettings.subtitles = e.target.checked;
    saveSettings();
});

loadSettings();
console.log('✅ BaixarYou pronto!');