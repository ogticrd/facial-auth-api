from typing import List
import cv2 as cv

from .landmarks import landmarks_detection
from .blink import blink_detection
from .blur import blur_detection
from .lbp import LocalBinaryPatterns

from ..config import RIGHT_EYE
from ..config import LEFT_EYE
from ..face_detection import get_face_from_frame

desc = LocalBinaryPatterns(24, 8)

def _verify_blink(total_blink: int) -> float:
    ratio: float = 0.10
    
    if total_blink < 3:
        ratio *= total_blink + 1
    elif total_blink == 3:
        ratio *= total_blink - 1
    
    return ratio

def verify_liveness(frames, closed_eyes_frames: int = 1) -> float:
    closed_eyes_frames_counter: int = 0
    total_blink: int = 0
    blur_per_frames: List[float] = []
    lbp_per_frames = []
        
    for frame in frames:
        ratio: int = 0
        
        color_face, gray_face = get_face_from_frame(frame, cmap='gray')
        
        fm = blur_detection(color_face)
        blur_per_frames.append(fm)
        
        lbp_value = desc.get_lbp_max(gray_face)
        lbp_per_frames.append(lbp_value)
        
        mesh_coords, check = landmarks_detection(frame)
        
        if check:
            ratio = blink_detection(mesh_coords, RIGHT_EYE, LEFT_EYE)
            if ratio > 5.3:
                closed_eyes_frames_counter += 1
            elif closed_eyes_frames_counter > closed_eyes_frames:
                total_blink += 1
                closed_eyes_frames_counter = 0
    
    blur_average = sum(blur_per_frames)/len(blur_per_frames)
    lbp_average = sum(lbp_per_frames)/len(lbp_per_frames)
    
    if total_blink > 5:
        alive_ratio = 0.0
    else:
        blink_ratio = _verify_blink(total_blink)
        
        alive_ratio: float = blink_ratio
        if blur_average <= 150.0:
            alive_ratio += 0.35
        
        if lbp_average > 0.050:
            alive_ratio += 0.35

    return {'alive_ratio': alive_ratio, 'total_blink': total_blink, 'blur_average': blur_average, 'lbp_average': lbp_average}