import mediapipe as mp
import numpy as np
import cv2 as cv

import time
import math
import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)))))

import face

WINDOW_NAME: str = 'Capture'
WIDTH: int = 640
HEIGHT: int = 480
CLOSED_EYES_FRAMES: int = 2
CLOSED_EYES_FRAMES_COUNTER: int = 0

cap: cv.VideoCapture = cv.VideoCapture(0)

# Set video resolution to 640x480
cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)

mp_face_mesh = mp.solutions.face_mesh
total_blink: int = 0

cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)

frame_counter: int = 0
start_time = time.time()

while cap.isOpened():
    frame_counter += 1
    ret, frame = cap.read()
    
    show_frame: np.ndarray = cv.flip(frame, 1)
    
    if not ret:
        break
    
    verified = True
    blinked = False
    ratio = 0
    # verified = face.verify(show_frame, './examples/target.jpeg')
    
    if verified:  
        mesh_coords, ret = face.liveness.landmarks.landmarks_detection(show_frame, False)
        if ret:
            ratio = face.liveness.blink.blink_detection(show_frame, mesh_coords, face.config.RIGHT_EYE, face.config.LEFT_EYE, tolerance=0.5)
            if ratio > 4.5:
                CLOSED_EYES_FRAMES_COUNTER += 1
                blinked = True
            elif CLOSED_EYES_FRAMES_COUNTER > CLOSED_EYES_FRAMES:
                total_blink += 1
                CLOSED_EYES_FRAMES_COUNTER = 0
                blinked = False
            else:
                blinked = False
            
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.FACE_OVAL], (247, 247, 247), 0.2)
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.LIPS], (250, 84, 72), 0.6)
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.LEFT_EYE], (34, 163, 99), 0.6)
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.RIGHT_EYE], (34, 163, 99), 0.6)
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.LEFT_EYEBROW], (144, 34, 163), 0.6)
            show_frame = face.draw.fill_polygon_transparent(show_frame, [mesh_coords[p] for p in face.config.RIGHT_EYEBROW], (144, 34, 163), 0.6)
    
    end_time = time.time() - start_time
    fps: float = frame_counter/end_time
    
    show_frame = cv.putText(show_frame, f'FPS: {round(fps, 2)},  verified: {verified}, Is alive: {"Yes" if total_blink > 0 and total_blink <= 5 else "No"}, total blink: {total_blink}, t: {math.floor(end_time % 5)}', (10, show_frame.shape[0] - 20), cv.FONT_HERSHEY_COMPLEX, 
                        0.6, (247, 247, 247), 2, cv.LINE_AA) 
    cv.imshow(WINDOW_NAME, show_frame)
    
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
    print(f'FPS: {fps}, blink ratio: {ratio}, End Time: {math.floor(end_time % 5)}, blinked: {blinked}')
    
    if (math.floor(end_time % 5)) == 0:
        total_blink = 0

cap.release()
cv.destroyWindow(WINDOW_NAME)