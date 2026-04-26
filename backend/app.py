from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
from pathlib import Path

# Forçar caminho do FFmpeg
os.environ['PATH'] += os.pathsep + 'D:\\ffmpeg-8.1-full_build\\bin'

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = Path(__file__).parent / "downloads"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Opções globais para o yt-dlp
YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': False,
    'ignoreerrors': True,
    'extract_flat': False,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'skip': ['hls', 'dash']
        }
    }
}

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '720p')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    # Mapeamento de qualidade - usando formatos mais simples
    quality_map = {
        'best': 'best',
        '1080p': 'best[height<=1080]',
        '720p': 'best[height<=720]',
        '480p': 'best[height<=480]',
        'audio': 'bestaudio'
    }
    
    try:
        ydl_opts = YDL_OPTS_BASE.copy()
        ydl_opts['outtmpl'] = str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s')
        ydl_opts['format'] = quality_map.get(quality, 'best[height<=720]')
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Encontrar o arquivo baixado
            filename = ydl.prepare_filename(info)
            if not Path(filename).exists():
                for f in DOWNLOAD_FOLDER.glob(f"{Path(filename).stem}.*"):
                    filename = str(f)
                    break
            
            # Limpar nome do arquivo
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', info.get('title', 'video'))
            ext = Path(filename).suffix[1:]
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{safe_title}.{ext}"
            )
            
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'Erro no YouTube: Pode ser necessário atualizar o yt-dlp. Detalhe: {str(e)[:150]}'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro: {str(e)[:150]}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'BaixarYou backend rodando!'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BaixarYou Backend (Versão Atualizada)")
    print("=" * 50)
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
    