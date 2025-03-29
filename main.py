from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid

app = FastAPI()

# ✅ Add this block right after creating `app`
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-ar-frontend-git-main-sirliboyevuzs-projects.vercel.app/"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/upload")
async def upload_file(image: UploadFile = File(...), video: UploadFile = File(...)):
    ar_id = str(uuid.uuid4())
    ar_dir = os.path.join(UPLOAD_DIR, ar_id)
    os.makedirs(ar_dir, exist_ok=True)

    with open(os.path.join(ar_dir, "target.jpg"), "wb") as img_file:
        shutil.copyfileobj(image.file, img_file)

    with open(os.path.join(ar_dir, "overlay.mp4"), "wb") as vid_file:
        shutil.copyfileobj(video.file, vid_file)

    return {"ar_url": f"/ar/{ar_id}"}


@app.get("/ar/{ar_id}", response_class=HTMLResponse)
async def serve_ar_viewer(ar_id: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>AR Viewer</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdn.jsdelivr.net/npm/aframe@1.2.0/dist/aframe.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/mind-ar@1.1.4/dist/mindar-image.prod.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/mind-ar@1.1.4/dist/aframe/mindar-image-aframe.prod.js"></script>
      <style>
        body, html {{ margin: 0; padding: 0; overflow: hidden; }}
        a-scene {{ width: 100vw; height: 100vh; }}
      </style>
    </head>
    <body>
      <a-scene mindar-image="imageTargetSrc: /uploads/{ar_id}/target.jpg;" 
               color-space="sRGB" embedded 
               device-orientation-permission-ui="enabled: true" 
               vr-mode-ui="enabled: false">
        <a-assets>
          <video id="video" src="/uploads/{ar_id}/overlay.mp4" autoplay loop muted playsinline></video>
        </a-assets>

        <a-camera position="0 0 0" look-controls="enabled: false"></a-camera>

        <a-entity mindar-image-target="targetIndex: 0">
          <a-video src="#video" width="1" height="0.6" position="0 0 0"></a-video>
        </a-entity>
      </a-scene>
    </body>
    </html>
    """

