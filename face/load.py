import numpy as np
import cv2 as cv

from typing import List
from typing import Optional
from typing import Tuple

def load_short_video(source: str, dims: Tuple[int, int] = (640, 480)) -> List[Optional[np.ndarray]]:
    frames: List[np.ndarray] = []
    
    cap: cv.VideoCapture = cv.VideoCapture(source)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, dims[0])
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, dims[1])
    
    if not cap.isOpened():
        # Improve error handle
        print('Error loading video.')
        return frames
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frames.append(frame)
    
    return frames