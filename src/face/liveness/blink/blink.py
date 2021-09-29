from typing import List
from typing import Tuple
import math

import numpy as np

def euclaidean_distance(point: Tuple[int, int], point1: Tuple[int, int]) -> float:
    x, y = point
    x1, y1 = point1
    return math.sqrt((x1 - x)**2 + (y1 - y)**2)

def blink_detection(img: np.ndarray, landmarks: List[Tuple[int, int]], right_indices: List[int], left_indices: List[int], tolerance: float):
    # Horizontal line
    re_h_right: Tuple[int, int] = landmarks[right_indices[0]]
    re_h_left: Tuple[int, int] = landmarks[right_indices[8]]
    
    le_h_right: Tuple[int, int] = landmarks[left_indices[0]]
    le_h_left: Tuple[int, int] = landmarks[left_indices[8]]
    
    # Vertical line
    re_v_top: Tuple[int, int] = landmarks[right_indices[12]]
    re_v_bottom: Tuple[int, int] = landmarks[right_indices[4]]
    
    le_v_top: Tuple[int, int] = landmarks[left_indices[12]]
    le_v_bottom: Tuple[int, int] = landmarks[left_indices[4]]
    
    # Horizontal Distance
    right_eye_h__distance = euclaidean_distance(re_h_right, re_h_left)
    left_eye_h_distance = euclaidean_distance(le_h_right, le_h_left)
    
    # Vertical Distance
    right_eye_v__distance = euclaidean_distance(re_v_top, re_v_bottom)
    left_eye_v_distance = euclaidean_distance(le_v_top, le_v_bottom)
    
    right_eye_ratio = right_eye_h__distance/right_eye_v__distance if right_eye_v__distance != 0.0 else 0.0
    left_eye_ratio = left_eye_h_distance/left_eye_v_distance if left_eye_v_distance != 0.0 else 0.0
    
    return (right_eye_ratio + left_eye_ratio) / 2