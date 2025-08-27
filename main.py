from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import uuid
import shutil

app = Flask(__name__)

# Paths for cookies
SECRET_COOKIES_SRC = "/etc/secrets/cookies.txt"   # Render secret (read-only)
COOKIE_COPY_PATH = "/tmp/cookies.txt"             # Writable copy for yt_dlp

# Copy cookies file into /tmp if available
if os.path.exists(SECRET_COOKIES_SRC):
    shutil.copy(SECRET_COOKIES_SRC, COOKIE_COPY_PATH)

# HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h2>📥 YouTube Downloader</h2>
    <form method="POST" action="/download">
        <input type="text" name="url" placeholder="Enter YouTube URL" size="50" required><br><br>
        <select name="choice">
            <option value="video">Download Video (MP4)</option>
            <option value="audio">Download Audio (MP3)</option>
        </select><br><br>
        <button type="submit">Download</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    choice = request.form.get("choice")
    unique_id = str(uuid.uuid4())
    download_dir = "/tmp/downloads"   # use /tmp because Render’s disk is read-only elsewhere
    os.makedirs(download_dir, exist_ok=True)

    # Common yt_dlp options
    base_opts = {
        'outtmpl': f'{download_dir}/{unique_id}.%(ext)s',
        'cookiefile': COOKIE_COPY_PATH if os.path.exists(COOKIE_COPY_PATH) else None
    }

    if choice == "video":
        ydl_opts = {
            **base_opts,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }
        expected_file = f"{download_dir}/{unique_id}.mp4"
    else:  # audio
        ydl_opts = {
            **base_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        expected_file = f"{download_dir}/{unique_id}.mp3"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        return send_file(expected_file, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
