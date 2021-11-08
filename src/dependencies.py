import os
import base64
import tempfile
from typing import List
from typing import Tuple
from typing import Union
import requests
import random

import numpy as np
import cv2 as cv

from config import HANDS_ACTIONS
from face.liveness import HandSign

def base64_to_webm(source: str) -> str:
    file_name: str = tempfile.mkstemp()[1] + '.webm'
    
    with open(file_name, 'wb') as video:
        video.write(base64.b64decode(source))
    
    return file_name

def load_short_video(source: str, dims: Tuple[int, int] = (640, 480)) -> List[np.ndarray]:
    frames: List[np.ndarray] = []
    
    cap: cv.VideoCapture = cv.VideoCapture(source)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, dims[0])
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, dims[1])
    
    if not cap.isOpened():
        raise IOError(f'Error reading video at {source}')
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frames.append(frame)
    
    return frames

def get_target_image(cedula: str) -> Union[str, int]:
    url = f'https://api.digital.gob.do/master/citizens/{cedula}/photo?api-key={os.environ.get("CEDULA_API_KEY")}'
    
    results = requests.get(url)
    
    results.raise_for_status()
    
    target_image_path = tempfile.mkstemp()[1] + '.jpg'
    
    f = open(target_image_path, 'wb')
    f.write(results.content)
    f.close()
    
    return target_image_path

def save_source_image(frames: List[np.ndarray]) ->  str:
    # get random frame from video
    frame = frames[random.randint(0, len(frames) - 1)]
    
    source_image_path = tempfile.mkstemp()[1] + '.jpg'
    
    cv.imwrite(source_image_path, frame)
    
    return source_image_path

def get_hand_action() -> HandSign:
    rand_action = random.randint(0, len(HANDS_ACTIONS) - 1)
    return HANDS_ACTIONS[rand_action]