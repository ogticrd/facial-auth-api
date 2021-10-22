import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from typing import List
import statistics
import numpy as np
import cv2 as cv

from .landmarks import landmarks_detection
from .blink import blink_detection
from .blur import blur_detection
from .lbp import LocalBinaryPatterns

from ..config import RIGHT_EYE
from ..config import LEFT_EYE
from ..face_detection import get_face_from_frame

from .hand import hand_sign_detection
from .hand import HandSignDetectionResult
from .hand import HandSign

class LivenessResult(TypedDict):
    is_alive: bool
    alive_ratio: float
    total_blink: int
    blur_average: float
    lbp_average: float

desc = LocalBinaryPatterns(24, 8)

def verify_liveness(frames: List[np.ndarray], hand_sign_action: HandSign, closed_eyes_frames: int = 1) -> LivenessResult:
    is_alive = False
    closed_eyes_frames_counter: int = 0
    total_blink: int = 0
    lbp_per_frames: List[float] = []
    hand_sign_result = {'frames': 0, 'hand': '', 'one_hand': True}
    
    for frame in frames:
        color_face, gray_face = get_face_from_frame(frame)
        if not color_face.size and not gray_face.size:
            return LivenessResult(is_alive=False, alive_ratio=0.0, total_blink=total_blink, blur_average=0.0, lbp_average=0.0)
        
        hand_output = hand_sign_detection(frame, hand_sign=hand_sign_action)
        
        if hand_output['result']:
            if hand_sign_result['frames'] == 0:
                hand_sign_result['hand'] = hand_output['hand']
        
            hand_sign_result['frames'] += 1
            hand_sign_result['one_hand'] = False if hand_sign_result['hand'] != hand_output['hand'] else True
        
        try:
            lbp_value = desc.get_lbp_max(gray_face)
            lbp_per_frames.append(lbp_value)
        except ValueError:
            pass
        
        mesh_coords, check = landmarks_detection(frame)
        
        if check:
            ratio = blink_detection(mesh_coords, RIGHT_EYE, LEFT_EYE)
        if ratio > 5.3:
            closed_eyes_frames_counter += 1
        elif closed_eyes_frames_counter > closed_eyes_frames:
            total_blink += 1
            closed_eyes_frames_counter = 0

    lbp_average = sum(lbp_per_frames)/len(lbp_per_frames)
    if (total_blink >= 0 and total_blink < 4) and (hand_sign_result['frames'] > 0 and hand_sign_result['one_hand']) and (lbp_average > 0.05):
        is_alive = True
    
    return LivenessResult(is_alive=is_alive, alive_ratio=0.0, total_blink=total_blink, blur_average=0.0, lbp_average=lbp_average)

# def _verify_blink(total_blink: int) -> float:
#     ratio: float = 0.10
    
#     if total_blink < 3:
#         ratio *= total_blink + 1
#     elif total_blink == 3:
#         ratio *= total_blink - 1
    
#     return ratio

# def verify_liveness(frames, hand_sign_action: HandSign, closed_eyes_frames: int = 1) -> float:
#     closed_eyes_frames_counter: int = 0
#     total_blink: int = 0
#     blur_per_frames: List[float] = []
#     lbp_per_frames = []
#     hand_sign_result = {'frames': 0, 'hand': '', 'one_hand': True}
        
#     for frame in frames:
#         ratio: int = 0
        
#         hand_output = hand_sign_detection(frame, hand_sign_action)
#         if hand_output['result']:
#             if hand_sign_result['frames'] == 0:
#                 hand_sign_result['hand'] = hand_output['hand']
#             else:
                
#         color_face, gray_face = get_face_from_frame(frame)
        
#         fm = blur_detection(color_face)
#         blur_per_frames.append(fm)
        
#         try:
#             lbp_value = desc.get_lbp_max(gray_face)
#         except ValueError:
#             pass
        
#         lbp_per_frames.append(lbp_value)
        
#         mesh_coords, check = landmarks_detection(frame)
        
#         if check:
#             ratio = blink_detection(mesh_coords, RIGHT_EYE, LEFT_EYE)
#             if ratio > 5.3:
#                 closed_eyes_frames_counter += 1
#             elif closed_eyes_frames_counter > closed_eyes_frames:
#                 total_blink += 1
#                 closed_eyes_frames_counter = 0
        
#     lbps_re = []
    
#     for i, value in enumerate(lbp_per_frames):
#         lbps_re.append(abs(lbp_per_frames[i] - lbp_per_frames[i-1]))
    
#     blur_average = sum(blur_per_frames)/len(blur_per_frames)
#     lbp_average = sum(lbp_per_frames)/len(lbp_per_frames)
#     lbps_re_average = sum(lbps_re)/len(lbps_re)
    
#     if total_blink > 5:
#         alive_ratio = 0.0
#     else:
#         blink_ratio = _verify_blink(total_blink)
        
#         alive_ratio: float = blink_ratio
#         # if blur_average <= 250.0:
#         #     alive_ratio += 0.35
        
#         # if lbp_average > 0.050:
#         #     alive_ratio += 0.35
        
#         alive_ratio += lbp_average * 10

#     return {'is_alive': True if alive_ratio > 0.5 else False, 'alive_ratio': alive_ratio, 'total_blink': total_blink, 'blur_average': blur_average, 'lbp_average': lbp_average, 'lbps_re_average': lbps_re_average}