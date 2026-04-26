from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
from pathlib import Path

os.environ['PATH'] += os.pathsep + 'D:\\ffmpeg-8.1-full_build\\bin'

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
    
    quality_map = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'audio': 'bestaudio/best'
    }
    
    try:
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s'),
            'format': quality_map.get(quality, 'bestvideo[height<=720]+bestaudio/best'),
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not Path(filename).exists():
                for f in DOWNLOAD_FOLDER.glob(f"{Path(filename).stem}.*"):
                    filename = str(f)
                    break
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{re.sub(r'[<>:\"/\\|?*]', '_', info.get('title', 'video'))}.mp4"
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 BaixarYou Backend")
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}")
    app.run(host='0.0.0.0', port=5000, debug=True)