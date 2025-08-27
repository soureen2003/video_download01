from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import yt_dlp
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube(url, only_audio=False):
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
    }
    if only_audio:
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })
    else:
        ydl_opts.update({"format": "best"})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h2>YouTube Downloader</h2>
    <form action="/download" method="post">
        <input type="text" name="url" placeholder="Enter YouTube URL" required>
        <button type="submit" name="type" value="video">Download Video</button>
        <button type="submit" name="type" value="audio">Download Audio</button>
    </form>
    """

@app.post("/download")
def download(url: str = Form(...), type: str = Form(...)):
    filepath = download_youtube(url, only_audio=(type == "audio"))
    return FileResponse(filepath, filename=os.path.basename(filepath))
