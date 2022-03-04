from typing import List
import numpy as np

from . import landmarks_detection
from . import blink_detection
from . import blur_detection
from . import LocalBinaryPatterns

from ..config import RIGHT_EYE
from ..config import LEFT_EYE
from ..face_detection import get_face_from_frame

from . import hand_sign_detection

from .types_utils import HandSign
from .types_utils import HandEnum
from .types_utils import LivenessResult
from .types_utils import HandSignResultValues

from src import logger

desc = LocalBinaryPatterns(24, 8)

def verify_liveness(frames: List[np.ndarray], hand_sign_action: HandSign, closed_eyes_frames: int = 1, min_num_frames_alive: int = 15) -> LivenessResult:
    is_alive = False
    closed_eyes_frames_counter: int = 0
    total_blink: int = 0
    lbp_per_frames: List[float] = []
    hand_sign_result = HandSignResultValues(frames=0, hand=HandEnum.right, one_hand=True)
    
    for frame in frames:
        color_face, gray_face = get_face_from_frame(frame)
        if not color_face.size and not gray_face.size:
            return LivenessResult(is_alive=False, alive_ratio=0.0, total_blink=total_blink, blur_average=0.0, lbp_average=0.0)
        
        hand_output = hand_sign_detection(frame, hand_sign=hand_sign_action)      
        
        if hand_output.result:
            if hand_sign_result.frames == 0:
                hand_sign_result.hand = hand_output.hand
        
            hand_sign_result.frames += 1
            hand_sign_result.one_hand = False if hand_sign_result.hand != hand_output.hand else True
        
        try:
            lbp_value = desc.get_lbp_max(gray_face)
            lbp_per_frames.append(lbp_value)
        except ValueError:
            pass
    
    logger.debug(f"frames alive: {hand_sign_result.frames} - hand: {hand_sign_result.hand}")

    total_blink = 0
    lbp_average = sum(lbp_per_frames)/len(lbp_per_frames)
    if (total_blink >= 0 and total_blink < 4) and (hand_sign_result.frames > min_num_frames_alive and hand_sign_result.one_hand):
        is_alive = True
    
    return LivenessResult(is_alive=is_alive, alive_ratio=0.0, total_blink=total_blink, blur_average=0.0, lbp_average=lbp_average)