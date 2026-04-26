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

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '720p')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    try:
        # Opções mais simples para evitar erros
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'format': 'best',  # Formato mais simples
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Procurar o arquivo baixado
            if not os.path.exists(filename):
                for f in os.listdir(DOWNLOAD_FOLDER):
                    if f.startswith(os.path.splitext(filename)[0]):
                        filename = os.path.join(DOWNLOAD_FOLDER, f)
                        break
            
            # Limpar nome do arquivo
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', info.get('title', 'video'))
            ext = os.path.splitext(filename)[1]
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{safe_title}{ext}"
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 BaixarYou Backend")
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5000, debug=True)