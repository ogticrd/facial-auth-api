import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import uvicorn
from fastapi import FastAPI
from fastapi import Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pydantic import Field

from .dependencies import base64_to_webm
from .dependencies import load_short_video
import face

class FaceAuthModel(BaseModel):
    cedula: str = Field(
        ..., 
        title="Document ID number", 
        max_length=11,
        min_length=11,
        regex='^([0-9]+)$'
    )
    source: str = Field(...,  title="Source to verify")

app = FastAPI(
    title='Facial Authentication API',
    description='An API to verify users using their faces and document ID (Cédula) photo.',
    version='0.1', 
    docs_url='/docs', 
    redoc_url='/redoc'
)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/', response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facial Authentication API</title>
    </head>
    <body>
        <video id="video" width="320" height="240" autoplay></video>
        <input type="text" id="cedulaInput" name="cedula" placeholder="No. Cedula" />
        <button id="start-record">Start Recording</button>
        <a id="download-video" download="test.webm">Download Video</a>
        <script src="/static/index.js"></script>
    </body>
    </html>
    """

@app.post('/verify')
def verify(data: FaceAuthModel = Body(..., embed=True)):
    video_path = base64_to_webm(data.source.split(',')[1])
    frames = load_short_video(video_path)
    print(len(frames))
    print(face.liveness.verify_liveness(frames))
    return { 'verified': False, 'face_verified': False, 'is_alive': False }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)