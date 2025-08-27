from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Folder for temporary downloads
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Path to cookies file (Render mounts secret file here if added)
COOKIES_PATH = "/etc/secrets/cookies.txt"

# Simple frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h2>YouTube Downloader</h2>
    <form method="POST" action="/download">
        <input type="text" name="url" placeholder="Enter YouTube URL" size="50" required><br><br>
        <select name="format">
            <option value="video">Video</option>
            <option value="audio">Audio Only</option>
        </select><br><br>
        <button type="submit">Download</button>
    </form>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_choice = request.form.get("format")

    if not url:
        return "No URL provided", 400

    # Generate unique file name
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

    # yt_dlp options
    ydl_opts = {
        "outtmpl": output_template,
    }

    # Use cookies if available
    if os.path.exists(COOKIES_PATH):
        ydl_opts["cookiefile"] = COOKIES_PATH

    if format_choice == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        ydl_opts["format"] = "best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # Adjust extension for mp3 audio
            if format_choice == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    # Render runs on 0.0.0.0:$PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
