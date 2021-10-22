import cv2 as cv
import numpy as np

from typing import List
from typing import Tuple

def fill_polygon_transparent(img: np.ndarray, points: List[Tuple[int, int]], color: Tuple[int, int, int], opacity: float) -> np.ndarray:
    list_to_np_array: np.ndarray = np.array(points, dtype=np.int32)
    
    overlay: np.ndarray = img.copy()
    
    cv.fillPoly(overlay,[list_to_np_array], color)
    
    new_img = cv.addWeighted(overlay, opacity, img, 1 - opacity, 0)
        
    img = new_img
    return img