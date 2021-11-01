import sys
import os
import uuid
from os.path import abspath, dirname, join

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from typing import Union
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import uvicorn
from fastapi import FastAPI
from fastapi import Body
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import requests
from rejson import Client
from rejson import Path

from dependencies import base64_to_webm
from dependencies import load_short_video
from dependencies import get_target_image
from dependencies import save_source_image
from dependencies import get_hand_action

from types.api import ChallengeResponse
from types.api import FaceAuthModel

import face

rj = Client(host=os.environ.get('REDIS_HOST', 'localhost'), port=os.environ.get('REDIS_PORT', 6379), decode_responses=True)

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
        <link rel="stylesheet" href="static/index.css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.9.0/p5.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.9.0/addons/p5.dom.min.js"></script>
        <script src="https://unpkg.com/ml5@latest/dist/ml5.min.js" type="text/javascript"></script>
        <title>Facial Authentication API</title>
    </head>
    <body>
        <h1>Face Recognition OGTIC Example</h1>
        <script src="/static/sketch.js"></script>
    </body>
    </html>
    """

@app.get('/challenge')
def challenge():
    id = uuid.uuid4()
    sign = get_hand_action()
    rj.jsonset(str(id), Path.rootPath(), sign)
    return ChallengeResponse(id=id, sign=sign)

@app.post('/verify')
def verify(data: FaceAuthModel = Body(..., embed=True)):
    video_path = base64_to_webm(data.source.split(',')[1])
    
    try:
        target_path = get_target_image(data.cedula)
    except requests.HTTPError:
        raise HTTPException(status_code=400, detail='Error trying to get cedula photo.')
    
    frames = load_short_video(video_path)
    source_path = save_source_image(frames)
    
    try:
        results_recog = face.verify(target_path, source_path)
    except IndexError:
        raise HTTPException(status_code=400, detail='Not face detected.')
    
    expected_sign  = rj.jsonget(data.id, Path.rootPath())
    if expected_sign:
        hand_sign_action = face.liveness.hand.HandSign(expected_sign)
        rj.jsondel(data.id, Path.rootPath())
    else:
        raise HTTPException(status_code=400, detail='Bad sign id.')
    
    results_live = face.liveness.verify_liveness(frames, hand_sign_action=hand_sign_action)
    
    return {'verified': True if results_recog['isIdentical'] and results_live['is_alive'] else False, 
            'face_verified': results_recog["isIdentical"], 
            'is_alive': results_live["is_alive"]}

if __name__ == "__main__":
    port: int = int(os.environ.get('PORT', 8080))
    host: str = os.environ.get('HOST', "localhost")
    uvicorn.run(app, host=host, port=port)