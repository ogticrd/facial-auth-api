import cv2

import mediapipe as mp
import matplotlib.pyplot as plt
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
import math
from typing import Union
from typing import Tuple
import numpy as np
from skimage import feature
from src.face.liveness.lbp import LocalBinaryPatterns
import requests

desc = LocalBinaryPatterns(24, 8)

blur_per_frames=[]
lbp_per_frames=[]
def _normalized_to_pixel_coordinates(
    normalized_x: float, normalized_y: float, image_width: int,
    image_height: int) -> Union[None, Tuple[int, int]]:
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


url = 'https://192.168.1.44:8080/shot.jpg'
# cap = cv2.VideoCapture(0)
with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
  while True:
    if len(blur_per_frames) >= 200:
        break
    raw_data = requests.get(url, verify=False)
    image_array = np.array(bytearray(raw_data.content), dtype=np.uint8)
    frame = cv2.imdecode(image_array, -1)
    image: np.ndarray = cv2.flip(frame, 1)

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = face_detection.process(image)

    # Draw the face detection annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.detections:
        face_locations = [] 
        for detection in results.detections:
            cords_1 = _normalized_to_pixel_coordinates(
                detection.location_data.relative_bounding_box.xmin, 
                detection.location_data.relative_bounding_box.ymin, 
                image.shape[1],
                image.shape[0])
            
            cords_2 = _normalized_to_pixel_coordinates(
                detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width, 
                detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height, 
                image.shape[1],
                image.shape[0])
            
            if cords_1 != None and cords_2 != None:
                xmin, ymin = cords_1
                xmax, ymax = cords_2
                
                face_locations.append((cords_1[0], cords_1[1], cords_2[0], cords_2[1]))

        xmin, ymin, xmax, ymax = max(face_locations, default=(0, 0, 0, 0), key=lambda x: (x[2]-x[0]) * (x[3]-x[1]))
        image = image[ymin:ymax, xmin:xmax]
        
        try:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lbp = desc.get_lbp_max(image)
            fm = cv2.Laplacian(image, cv2.CV_64F).var()
        except:
            continue
        
        lbp_per_frames.append(lbp)
        blur_per_frames.append(fm)
    
    if (not image.shape[0] and not image.shape[1]):
        continue
    
    cv2.imshow('MediaPipe Face Detection', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break
print(f'Average blur per frames: {sum(blur_per_frames)/len(blur_per_frames)}')
print(f'Local binary pattern max per frames: {sum(lbp_per_frames)/len(lbp_per_frames)}')