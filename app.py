from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Pasta para downloads temporários
DOWNLOAD_FOLDER = Path(__file__).parent / "downloads"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

def sanitize_filename(filename):
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'BaixarYou API está funcionando!', 'status': 'online'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'BaixarYou backend rodando!'})

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', '720p')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    # Mapeamento de qualidade
    quality_map = {
        'best': 'best',
        '1080p': 'best[height<=1080]',
        '720p': 'best[height<=720]',
        '480p': 'best[height<=480]',
        'audio': 'bestaudio'
    }
    
    try:
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'format': quality_map.get(quality, 'best[height<=720]'),
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Procurar o arquivo baixado
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for f in os.listdir(DOWNLOAD_FOLDER):
                    if f.startswith(base) or f.startswith(sanitize_filename(info.get('title', 'video'))):
                        filename = os.path.join(DOWNLOAD_FOLDER, f)
                        break
            
            safe_title = sanitize_filename(info.get('title', 'video'))
            ext = os.path.splitext(filename)[1]
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{safe_title}{ext}"
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BaixarYou Backend")
    print("=" * 50)
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)