from typing import Tuple
from typing import List
from typing import Optional
import math

import mediapipe as mp
import numpy as np
import cv2 as cv

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def _normalized_to_pixel_coordinates(
        normalized_x: float, normalized_y: float, image_width: int,
        image_height: int) -> Optional[Tuple[int, int]]:
    """Converts normalized value pair to pixel coordinates."""

    # Checks if the float value is between 0 and 1.
    def is_valid_normalized_value(value: float) -> bool:
        return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                        math.isclose(1, value))

    if not (is_valid_normalized_value(normalized_x) and
            is_valid_normalized_value(normalized_y)):
        return None
    
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px

def get_face_from_frame(frame: np.ndarray, model_selection: int = 0, min_detection_confidence: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    with mp_face_detection.FaceDetection(
    model_selection=model_selection, min_detection_confidence=min_detection_confidence) as face_detection:
        frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
        frame.flags.writeable = False
        
        results = face_detection.process(frame)
        
        face_locations: List[Tuple[int, int, int, int]] = []
        
        frame.flags.writeable = True
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        
        if results.detections:
            for detection in results.detections:
                cords_1 = _normalized_to_pixel_coordinates(
                    detection.location_data.relative_bounding_box.xmin, 
                    detection.location_data.relative_bounding_box.ymin, 
                    frame.shape[1],
                    frame.shape[0])
                
                cords_2 = _normalized_to_pixel_coordinates(
                    detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width, 
                    detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height, 
                    frame.shape[1],
                    frame.shape[0])
                
                if cords_1 != None and cords_2 != None:
                    face_locations.append((cords_1[0], cords_1[1], cords_2[0], cords_2[1])) # type: ignore
        
        xmin, ymin, xmax, ymax = max(face_locations, default=(0, 0, 0, 0), key=lambda x: (x[2]-x[0]) * (x[3]-x[1]))
        color_face = frame[ymin:ymax, xmin:xmax]
        
        gray_face = color_face if 0 in color_face.shape else cv.cvtColor(color_face, cv.COLOR_BGR2GRAY)
        
        return color_face, gray_face