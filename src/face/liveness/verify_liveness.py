from typing import List

from .landmarks import landmarks_detection
from .blink import blink_detection
from .blur import blur_detection

from ..config import RIGHT_EYE
from ..config import LEFT_EYE

def _verify_blink(total_blink: int) -> float:
    ratio: float = 0.16
    
    if total_blink < 3:
        ratio *= total_blink + 1
    elif total_blink == 3:
        ratio *= total_blink - 1
    
    return ratio

def verify_liveness(frames, closed_eyes_frames: int = 1) -> float:
    closed_eyes_frames_counter: int = 0
    total_blink: int = 0
    blur_per_frames: List[float] = []
        
    for frame in frames:
        ratio: int = 0
        
        fm = blur_detection(frame)
        blur_per_frames.append(fm)
        
        mesh_coords, check = landmarks_detection(frame)
        
        if check:
            ratio = blink_detection(frame, mesh_coords, RIGHT_EYE, LEFT_EYE, tolerance=0.5)
            if ratio > 4.5:
                closed_eyes_frames_counter += 1
            elif closed_eyes_frames_counter > closed_eyes_frames:
                total_blink += 1
                closed_eyes_frames_counter = 0
    
    blur_average = sum(blur_per_frames)/len(blur_per_frames)
    blink_ratio = _verify_blink(total_blink)
    
    alive_ratio: float = blink_ratio
    if blur_average <= 100.0:
        alive_ratio += blur_average
    
    return {'alive_ratio': alive_ratio, 'total_blink': total_blink, 'blur_average': blur_average}