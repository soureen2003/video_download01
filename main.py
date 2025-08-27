from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

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
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    if choice == "video":
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{download_dir}/{unique_id}.%(ext)s'
        }
    else:  # audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_dir}/{unique_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if choice == "video":
                filename = f"{unique_id}.mp4"
            else:
                filename = f"{unique_id}.mp3"
            filepath = os.path.join(download_dir, filename)

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
