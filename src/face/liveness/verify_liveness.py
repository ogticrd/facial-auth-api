from .landmarks import landmarks_detection
from .blink import blink_detection
from ..config import RIGHT_EYE
from ..config import LEFT_EYE

def verify_liveness(frames, closed_eyes_frames: int = 1):
    closed_eyes_frames_counter: int = 0
    total_blink: int = 0
    
    for frame in frames:
        ratio = 0
        mesh_coords, check = landmarks_detection(frame)
        
        if check:
            ratio = blink_detection(frame, mesh_coords, RIGHT_EYE, LEFT_EYE, tolerance=0.5)
            if ratio > 4.5:
                closed_eyes_frames_counter += 1
            elif closed_eyes_frames_counter > closed_eyes_frames:
                total_blink += 1
                closed_eyes_frames_counter = 0
    
    return {'total_blink': total_blink}