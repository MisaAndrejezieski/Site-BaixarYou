const BACKEND_URL = 'http://localhost:5000';

async function baixarVideo(url) {
    const progressDiv = document.getElementById('downloadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressTitle = document.getElementById('progressTitle');
    
    progressDiv.style.display = 'block';
    progressTitle.textContent = 'Baixando...';
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, quality: '720p' })
        });
        
        if (response.ok) {
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
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erro no download');
        }
        
    } catch (error) {
        progressDiv.style.display = 'none';
        alert('❌ Erro: ' + error.message);
    }
}

// Evento do botão
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

console.log('✅ BaixarYou pronto!');