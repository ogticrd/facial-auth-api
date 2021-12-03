import sys
import os
import uuid
import json
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import uvicorn
from fastapi import FastAPI
from fastapi import Body
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import socketio
from loguru import logger
import requests
import redis

from dependencies import base64_to_webm
from dependencies import load_short_video
from dependencies import get_target_image
from dependencies import save_source_image
from dependencies import get_hand_action

from types_utils import ChallengeResponse
from types_utils import ChallengeCache
from types_utils import VerifyResponse
from types_utils import FaceAuthModel
from types_utils import SocketErrorResult

import face

# logs
log_dir = os.environ.get('LOG_DIR', './logs/')
logger.add(os.path.join(log_dir, 'file_{time}.log'))

r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)))

app = FastAPI(
    docs_url='/docs', 
    redoc_url='/redoc'
)

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
        <script src="/static/sketch.js"></script>
    </body>
    </html>
    """

@app.get('/challenge', response_model=ChallengeResponse)
def challenge():
    id = uuid.uuid4()
    sign = get_hand_action()
    challenge_cache = ChallengeCache(sign=sign, sid=None, trial=0)
    r.set(str(id), json.dumps(challenge_cache.dict()))
    return ChallengeResponse(id=id, sign=sign)

@app.post('/verify', response_model=VerifyResponse)
def verify(data: FaceAuthModel = Body(..., embed=True)):
    video_path = base64_to_webm(data.source.split(',')[1])
    
    logger.debug(f"Video temporarily saved at {video_path}")
    
    try:
        target_path = get_target_image(data.cedula)
    except requests.HTTPError:
        logger.error(f"Error trying to get cedula photo - Something had occur at src.dependencies.get_target_image.")
        raise HTTPException(status_code=400, detail='Error trying to get cedula photo.')
    
    frames = load_short_video(video_path)
    source_path = save_source_image(frames)
    
    try:
        results_recog = face.verify(target_path, source_path)
    except IndexError:
        logger.error(f"Not face detected - Somthing had occur at src.face.verify")
        raise HTTPException(status_code=400, detail='Not face detected.')
    
    challenge_cache_data = r.get(data.id)
    if challenge_cache_data:
        challenge_cache = ChallengeCache(**json.loads(challenge_cache_data))
        hand_sign_action = challenge_cache.sign
        r.delete(data.id)
    else:
        logger.error(f"Invalid sign id - Sign id does not exit in redis")
        raise HTTPException(status_code=400, detail='Invalid sign id.')
    
    results_live = face.liveness.verify_liveness(frames, hand_sign_action=hand_sign_action)
    
    logger.error(f"User: {data.cedula} - verified: {True if results_recog.isIdentical and results_live.is_alive else False} - face_verified: {results_recog.isIdentical} - Is alive: {results_live.is_alive}")
    return VerifyResponse(
        verified=True if results_recog.isIdentical and results_live.is_alive else False,
        face_verified=results_recog.isIdentical,
        is_alive=results_live.is_alive
    )

# Socket.io events

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.on('verify')
async def verify_io(sid, data):
    logger.debug(f'Executing verify... SID: {sid}')
    try:
        data = FaceAuthModel(**data)
        logger.debug(f'Executing verify with data verified! SID: {sid}')
    except ValidationError:
        logger.error(f"Input data is not valid. SID: {sid}")
        await sio.emit('result', dict(SocketErrorResult(error='Input data is not valid')))
        r.delete(data.id)
        return
    
    video_path = base64_to_webm(data.source.split(',')[1])
    
    logger.debug(f"Video temporarily saved at {video_path}. SID: {sid}")
    
    try:
        target_path = get_target_image(data.cedula)
    except requests.HTTPError:
        logger.error(f"Error trying to get cedula photo - Something had occur at src.dependencies.get_target_image. SID: {sid}")
        await sio.emit('result', dict(SocketErrorResult(error='Error trying to get cedula')))
        r.delete(data.id)
        return
    
    frames = load_short_video(video_path)
    source_path = save_source_image(frames)
    
    logger.debug(f"Source image temporarily saved at {source_path}. SID: {sid}")
    
    challenge_cache_data = r.get(data.id)
    if challenge_cache_data:
        logger.debug(f"Retrive challenge cache. SID: {sid}")
        challenge_cache = ChallengeCache(**json.loads(challenge_cache_data))
        hand_sign_action = challenge_cache.sign
        if not challenge_cache.sid:
            logger.debug(f"Add sid to challenge cache. SID: {sid}")
            challenge_cache.sid = sid
        
        if challenge_cache.sid != sid:
            logger.error(f"Invalid sign id - Challenge cache SID ({challenge_cache.sid}) do not match with SID ({sid}). SID: {sid}")
            await sio.emit('result', dict(SocketErrorResult(error='Invalid sign id. in sid')))
            r.delete(data.id) 
            return
        
        if challenge_cache.trial >= 20:
            logger.error(f"Number of trial exceeded. SID: {sid}")
            await sio.emit('result', dict(SocketErrorResult(error='Number of trial exceeded.')))
            r.delete(data.id)
            return
        else:
            challenge_cache.trial += 1
            r.set(str(data.id), json.dumps(challenge_cache.dict()))
    else:
        logger.error(f"Invalid sign id - Sign id does not exit in redis. SID: {sid}")
        await sio.emit('result', dict(SocketErrorResult(error='Invalid sign id.')))
        r.delete(data.id)
        return
    results_live = face.liveness.verify_liveness(frames, hand_sign_action=hand_sign_action)
    logger.debug(f"Liveness Verified! SID: {sid}")
    if results_live.is_alive:
        logger.debug(f"verify if it is alive! SID: {sid}")
        try:
            results_recog = face.verify(target_path, source_path)
        except IndexError:
            logger.error(f"Not face detected - Somthing had occur at src.face.verify SID: {sid}")
            await sio.emit('result', dict(SocketErrorResult(error='Not face detected')))
            r.delete(data.id)
            return
    else:
        logger.debug(f"verify if it is not alive! SID: {sid}")
        results_recog = face.VerifyResult(isIdentical=False, confidence=0.0)
    
    logger.info(f"User: {data.cedula} - verified: {True if results_recog.isIdentical and results_live.is_alive else False} - face_verified: {results_recog.isIdentical} - Is alive: {results_live.is_alive}")

    result = VerifyResponse(
        verified=True if results_recog.isIdentical and results_live.is_alive else False,
        face_verified=results_recog.isIdentical,
        is_alive=results_live.is_alive
    )
    
    await sio.emit('result', dict(result), to=sid)
    logger.debug(f'Sent to result! SID: {sid}')

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == "__main__":
    port: int = int(os.environ.get('PORT', 8080))
    host: str = os.environ.get('HOST', 'localhost')
    uvicorn.run(socketio_app, host=host, port=port)
