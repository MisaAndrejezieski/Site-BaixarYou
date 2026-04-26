// URL do backend no Render
const BACKEND_URL = 'https://site-baixaryou.onrender.com';

// Configurações do usuário
let userSettings = {
    format: 'mp4',
    quality: '720p',
    subtitles: false
};

// Carregar configurações salvas
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

// Salvar configurações
function saveSettings() {
    localStorage.setItem('baixaryou_settings', JSON.stringify(userSettings));
}

// Função para baixar vídeo
async function baixarVideo(url) {
    const progressDiv = document.getElementById('downloadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressTitle = document.getElementById('progressTitle');
    const progressSpeed = document.getElementById('progressSpeed');
    
    progressDiv.style.display = 'block';
    progressTitle.textContent = 'Conectando ao servidor...';
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    progressSpeed.textContent = 'Aguarde...';
    
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
            const error = await response.json();
            throw new Error(error.error || 'Erro no download');
        }
        
        progressTitle.textContent = 'Baixando vídeo...';
        progressFill.style.width = '70%';
        progressPercent.textContent = '70%';
        progressSpeed.textContent = 'Processando...';
        
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
        progressTitle.textContent = 'Download concluído!';
        progressSpeed.textContent = 'Arquivo salvo!';
        
        setTimeout(() => {
            progressDiv.style.display = 'none';
        }, 3000);
        
    } catch (error) {
        progressDiv.style.display = 'none';
        alert('❌ Erro: ' + error.message);
    }
}

// Eventos
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

// Botão de download
document.getElementById('downloadBtn')?.addEventListener('click', () => {
    const url = document.getElementById('urlInput').value.trim();
    if (url) {
        baixarVideo(url);
    } else {
        alert('Cole uma URL válida');
    }
});

// Enter key
document.getElementById('urlInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('downloadBtn').click();
    }
});

// Menu mobile
document.querySelector('.menu-toggle')?.addEventListener('click', () => {
    document.querySelector('.nav-menu').classList.toggle('active');
});

// Scroll suave
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
});

// Carregar configurações
loadSettings();
console.log('✅ BaixarYou pronto! Backend:', BACKEND_URL);