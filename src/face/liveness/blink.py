from typing import List
from typing import Tuple

from scipy.spatial import distance

def blink_detection(landmarks: List[Tuple[int, int]], right_indices: List[int], left_indices: List[int]):
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
    right_eye_h__distance = distance.euclidean(re_h_right, re_h_left)
    left_eye_h_distance = distance.euclidean(le_h_right, le_h_left)
    
    # Vertical Distance
    right_eye_v__distance = distance.euclidean(re_v_top, re_v_bottom)
    left_eye_v_distance = distance.euclidean(le_v_top, le_v_bottom)
    
    right_eye_ratio = right_eye_h__distance/right_eye_v__distance if right_eye_v__distance != 0.0 else 0.0
    left_eye_ratio = left_eye_h_distance/left_eye_v_distance if left_eye_v_distance != 0.0 else 0.0
    
    return (right_eye_ratio + left_eye_ratio) / 2