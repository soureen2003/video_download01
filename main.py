import os
import shutil
from flask import Flask, request, send_file, render_template_string
import yt_dlp

app = Flask(__name__)

# Copy cookies.txt to a writable directory (/tmp)
COOKIE_SRC = "/etc/secrets/cookies.txt"
COOKIE_DST = "/tmp/cookies.txt"
if os.path.exists(COOKIE_SRC):
    shutil.copy(COOKIE_SRC, COOKIE_DST)
else:
    COOKIE_DST = None  # fallback if no cookies provided

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body>
    <h2>YouTube Video/Audio Downloader</h2>
    <form method="POST" action="/download">
        <input type="text" name="url" placeholder="Enter YouTube URL" required>
        <select name="format">
            <option value="video">Video (mp4)</option>
            <option value="audio">Audio (mp3)</option>
        </select>
        <button type="submit">Download</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    format_type = request.form["format"]

    output_file = "/tmp/output.%(ext)s"

    ydl_opts = {
        "outtmpl": output_file,
    }

    if COOKIE_DST:
        ydl_opts["cookiefile"] = COOKIE_DST

    if format_type == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": "/tmp/output.%(ext)s",
        })
    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "/tmp/output.%(ext)s",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == "audio":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            else:
                filename = filename.rsplit(".", 1)[0] + ".mp4"

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
