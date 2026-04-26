from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
from pathlib import Path

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = Path(__file__).parent / "downloads"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

def sanitize_filename(filename):
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    try:
        # Opções do yt-dlp
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Baixar o vídeo
            info = ydl.extract_info(url, download=True)
            
            # Encontrar o arquivo baixado
            filename = ydl.prepare_filename(info)
            
            # Se não encontrar, procurar na pasta
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for f in os.listdir(DOWNLOAD_FOLDER):
                    if f.startswith(base) or f.startswith(sanitize_filename(info.get('title', 'video'))):
                        filename = os.path.join(DOWNLOAD_FOLDER, f)
                        break
            
            # Verificar se o arquivo existe
            if not os.path.exists(filename):
                return jsonify({'error': 'Arquivo não encontrado após download'}), 500
            
            # Nome seguro para download
            safe_title = sanitize_filename(info.get('title', 'video'))
            ext = os.path.splitext(filename)[1]
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{safe_title}{ext}"
            )
            
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'BaixarYou backend rodando!'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BaixarYou Backend")
    print("=" * 50)
    print(f"📁 Downloads salvos em: {DOWNLOAD_FOLDER}")
    print("🌐 Servidor rodando em: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
    