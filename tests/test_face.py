import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import unittest

import numpy as np

import face

class TestFace(unittest.TestCase):
    def setUp(self):
        self.dims = (640, 480)
        
        self.frame = np.random.random((self.dims[0], self.dims[1], 3)) * 255
        self.frame = self.frame.astype('uint8')
    
    def test_get_face_from_frame(self):
        results = face.get_face_from_frame(frame=self.frame, model_selection=0, min_detection_confidence=0.5)
        self.assertEqual(type(results), tuple)
        self.assertEqual(type(results[0]), np.ndarray)
        self.assertEqual(type(results[1]), np.ndarray)