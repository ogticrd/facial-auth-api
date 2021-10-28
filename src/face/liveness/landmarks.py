import mediapipe as mp
import numpy as np
import cv2 as cv

from typing import List
from typing import Tuple

mp_face_mesh = mp.solutions.face_mesh

def _get_landmarks_coord(frame: np.ndarray, results, draw: bool = False) -> List[Tuple[int, int]]:
    img_height, img_width= frame.shape[:2]
    
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv.circle(frame, p, 2, (66, 255, 148), -1) for p in mesh_coord]

    return mesh_coord

def landmarks_detection(frame: np.ndarray, draw: bool = False) -> Tuple[List[Tuple[int, int]], bool]:
    with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    min_tracking_confidence=0.5,
    min_detection_confidence=0.5) as face_mesh:
        frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
        frame.flags.writeable = False
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
            return _get_landmarks_coord(frame, results, draw=draw), True

        return list(), False