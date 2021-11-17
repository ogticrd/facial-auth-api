# import sys
# import os
# import uuid
# import json
# from os.path import abspath, dirname, join
# sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

# import uvicorn
# from fastapi import FastAPI
# from fastapi import WebSocket
# from fastapi import WebSocketDisconnect
# from fastapi import Body
# from fastapi import HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse
# from starlette.middleware.cors import CORSMiddleware
# from loguru import logger
# import requests
# import redis

# from dependencies import base64_to_webm
# from dependencies import load_short_video
# from dependencies import get_target_image
# from dependencies import save_source_image
# from dependencies import get_hand_action

# from src.websocket import VerifyConnectionManager

# from types_utils import ChallengeResponse
# from types_utils import VerifyResponse
# from types_utils import VerifyRequestModel

# import face

# # logs
# log_dir = os.environ.get('LOG_DIR', './logs/')
# logger.add(os.path.join(log_dir, 'file_{time}.log'))

# r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)))

# app = FastAPI(
#     title='Facial Authentication API',
#     description='An API to verify users using their faces and document ID (Cédula) photo.',
#     version='0.1', 
#     docs_url='/docs', 
#     redoc_url='/redoc'
# )

# # Websocket manager
# verify_manager = VerifyConnectionManager()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_origin_regex='https?://.*',
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.mount('/static', StaticFiles(directory='static'), name='static')

# @app.get('/', response_class=HTMLResponse)
# def root():
#     return """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta http-equiv="X-UA-Compatible" content="IE=edge">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <link rel="stylesheet" href="static/index.css" />
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.9.0/p5.min.js"></script>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/0.9.0/addons/p5.dom.min.js"></script>
#         <script src="https://unpkg.com/ml5@latest/dist/ml5.min.js" type="text/javascript"></script>
#         <title>Facial Authentication API</title>
#     </head>
#     <body>
#         <h1>Face Recognition OGTIC Example</h1>
#         <script src="/static/sketch.js"></script>
#     </body>
#     </html>
#     """

# @app.get('/challenge', response_model=ChallengeResponse)
# def challenge():
#     id = uuid.uuid4()
#     sign = get_hand_action()
#     r.set(str(id), json.dumps(dict(sign)))
#     return ChallengeResponse(id=id, sign=sign)

# @app.post('/verify', response_model=VerifyResponse)
# def verify(data: VerifyRequestModel = Body(..., embed=True)):
#     video_path = base64_to_webm(data.source.split(',')[1])
    
#     logger.debug(f"Video temporarily saved at {video_path}")
    
#     try:
#         target_path = get_target_image(data.cedula)
#     except requests.HTTPError:
#         logger.error(f"Error trying to get cedula photo - Something had occur at src.dependencies.get_target_image.")
#         raise HTTPException(status_code=400, detail='Error trying to get cedula photo.')
    
#     frames = load_short_video(video_path)
#     source_path = save_source_image(frames)
    
#     try:
#         results_recog = face.verify(target_path, source_path)
#     except IndexError:
#         logger.error(f"Not face detected - Somthing had occur at src.face.verify")
#         raise HTTPException(status_code=400, detail='Not face detected.')
    
#     challenge = r.get(data.id)
#     if challenge:
#         expected_sign = json.loads(challenge)
#         hand_sign_action = face.liveness.HandSign(**expected_sign)
#         r.delete(data.id)
#     else:
#         logger.error(f"Invalid sign id - Sign id does not exit in redis")
#         raise HTTPException(status_code=400, detail='Invalid sign id.')
    
#     results_live = face.liveness.verify_liveness(frames, hand_sign_action=hand_sign_action)
    
#     logger.error(f"User: {data.cedula} - verified: {True if results_recog.isIdentical and results_live.is_alive else False} - face_verified: {results_recog.isIdentical} - Is alive: {results_live.is_alive}")
#     return VerifyResponse(
#         verified=True if results_recog.isIdentical and results_live.is_alive else False,
#         face_verified=results_recog.isIdentical,
#         is_alive=results_live.is_alive
#     )

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")

# @app.websocket('/verify')
# async def websocket_verify(websocket: WebSocket):
#     await verify_manager.connect(websocket)
#     try:
#         while True:
#             data = await verify_manager.receive(websocket)
#             await verify_manager.send(websocket, dict(data))
#     except WebSocketDisconnect:
#         await verify_manager.disconnect(websocket)

# if __name__ == "__main__":
#     port: int = int(os.environ.get('PORT', 8080))
#     host: str = os.environ.get('HOST', "localhost")
#     uvicorn.run(app, host=host, port=port)

import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

socketio_app = socketio.ASGIApp(sio, app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.on('message')
async def chat_message(sid, data):
    print("message ", data)
    await sio.emit('response', 'hi ' + data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@app.get("/v2")
def read_main():
    return {"message": "Hello World"}