import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import unittest
import numpy as np
import cv2 as cv

import face

class TestLiviness(unittest.TestCase):
    def setUp(self) -> None:
        self.num_landmarks_points = 468
        self.dims = (640, 480)
        
        self.frame = np.random.random((self.dims[0], self.dims[1], 3)) * 255
        self.frame = self.frame.astype('uint8')
    
    def test_landmarks_detection(self):
        results = face.liveness.landmarks_detection(frame=self.frame, draw=False)
        self.assertEqual(type(results), tuple)
        self.assertEqual(type(results[0]), list)
        self.assertEqual(type(results[1]), bool)

    def test_blink(self):
        landmarks = [(0, 0)] * self.num_landmarks_points
        blink_ratio = face.liveness.blink_detection(landmarks, face.config.RIGHT_EYE, face.config.LEFT_EYE)
        self.assertEqual(type(blink_ratio), float)
        self.assertEqual(blink_ratio, 0.0)
    
    def test_blur(self):
        blur_ratio = face.liveness.blur_detection(frame=self.frame)
        self.assertEqual(type(blur_ratio), np.float64)
    
    def test_lbp(self):
        gray_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
        lbp = face.liveness.LocalBinaryPatterns(24, 8)
        lbp_ratio = lbp.get_lbp_max(gray_frame)
        self.assertEqual(type(lbp_ratio), np.float64)