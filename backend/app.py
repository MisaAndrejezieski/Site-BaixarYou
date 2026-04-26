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
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    try:
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
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

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    os.environ['WERKZEUG_DEBUG_PIN'] = 'off'  # Desativa o PIN
    print("🚀 BaixarYou Backend")
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
    