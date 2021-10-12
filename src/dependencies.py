import base64
import tempfile
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import cv2 as cv

def base64_to_webm(source: str) -> str:
    file_name: str = tempfile.mkstemp()[1] + '.webm'
    print(file_name)
    with open(file_name, 'wb') as video:
        video.write(base64.b64decode(source))
    
    return file_name

def load_short_video(source: str, dims: Tuple[int, int] = (640, 480)) -> List[Optional[np.ndarray]]:
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