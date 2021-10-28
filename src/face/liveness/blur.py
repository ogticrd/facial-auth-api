import numpy as np
import cv2 as cv

def blur_detection(frame: np.ndarray) -> np.float64:
        fm: np.float64
        
        try:
            fm = cv.Laplacian(frame, cv.CV_64F).var()
        except:
            fm = np.float64(200.0)
        
        return fm