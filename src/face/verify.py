from numpy.core.numeric import Inf
# import face_recognition
import numpy as np
import cv2 as cv

from typing import Union
from typing import Tuple

def verify(unknown: Union[np.ndarray, str], target: Union[np.ndarray, str], max_num_faces=1, tolerance: float = 0.4) -> bool:
    unknown = cv.resize(unknown, (0, 0), fx=0.25, fy=0.25)
    
    target_image: np.ndarray = face_recognition.load_image_file(target)
    target_face_encoding = face_recognition.face_encodings(target_image)[0]
    
    face_locations: Tuple[int, int, int, int] = face_recognition.face_locations(unknown)

    if (max_num_faces != Inf) and ((len(face_locations) > max_num_faces) or (len(face_locations) == 0)):
        return False
    
    face_encodings = face_recognition.face_encodings(unknown, face_locations)[0]
    
    return face_recognition.compare_faces([target_face_encoding], face_encodings, tolerance=tolerance)[0]