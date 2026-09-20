import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class DownloadRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/download")
def download(req: DownloadRequest):
    file_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "best",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not os.path.exists(filename):
        raise HTTPException(status_code=500, detail="Download failed")

    return FileResponse(filename, filename=os.path.basename(filename))