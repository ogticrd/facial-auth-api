import os
import json

from fastapi import WebSocket
from fastapi import status
from loguru import logger
import requests
import redis

from src.websocket._manager import IConnectionManager
from src.types_utils import VerifyResponse
from src.types_utils import VerifyRequestModel

from src.dependencies import base64_to_webm
from src.dependencies import load_short_video
from src.dependencies import get_target_image
from src.dependencies import save_source_image
from src.dependencies import get_hand_action
from src import face

r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=int(os.environ.get('REDIS_PORT', 6379)))

class VerifyConnectionManager(IConnectionManager):
    def __init__(self) -> None:
        super().__init__()
    
    async def receive(self, websocket: WebSocket) -> VerifyResponse:
        raw_data = await websocket.receive_json()
        
        # Data validation
        data = VerifyRequestModel(**raw_data)
        
        video_path = base64_to_webm(data.source.split(',')[1])
        
        logger.debug(f'Capture type header: {data.source.split(",")[0]}')
        logger.debug(f'Capture video path: {video_path}')
    
        logger.debug(f"Video temporarily saved at {video_path}")
        
        try:
            target_path = get_target_image(data.cedula)
        except requests.HTTPError:
            logger.error(f"Error trying to get cedula photo - Something have occur at src.dependencies.get_target_image.")
            self.send(websocket, data={"error": "Error trying to get cedula photo"})
            self.disconnect(websocket, code=status.WS_1005_ABNORMAL_CLOSURE)
        
        frames = load_short_video(video_path)
        source_path = save_source_image(frames)
        
        logger.debug(f'Source image path: {source_path}')
        
        return {'name': 'Nami'}
        
        # try:
        #     results_recog = face.verify(target_path, source_path)
        # except IndexError:
        #     logger.error(f"Not face detected - Somthing have occur at src.face.verify")
        #     self.send(websocket, data={"error": "Not face detected"})
        #     self.disconnect(websocket, code=status.WS_1005_ABNORMAL_CLOSURE)
        
        # challenge = r.get(data.id)
        # if challenge:
        #     expected_sign = json.loads(challenge)
        #     hand_sign_action = face.liveness.HandSign(**expected_sign)
        #     r.delete(data.id)
        # else:
        #     logger.error(f"Invalid sign id - Sign id does not exit in redis")
        #     self.send(websocket, data={"error": "Invalid sign id"})
        #     self.disconnect(websocket, code=status.WS_1005_ABNORMAL_CLOSURE)
        
        # results_live = face.liveness.verify_liveness(frames, hand_sign_action=hand_sign_action)
        
        # logger.error(f"User: {data.cedula} - verified: {True if results_recog.isIdentical and results_live.is_alive else False} - face_verified: {results_recog.isIdentical} - Is alive: {results_live.is_alive}")
        # return VerifyResponse(
        #     verified=True if results_recog.isIdentical and results_live.is_alive else False,
        #     face_verified=results_recog.isIdentical,
        #     is_alive=results_live.is_alive
        # )
    
    async def send(self, websocket: WebSocket, data: dict) -> None:
        await websocket.send_json(data)