import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import random
import unittest

import numpy as np

import face

class TestFace(unittest.TestCase):
    def setUp(self) -> None:
        self.dims = (640, 480)
        
        self.frame = np.random.random((self.dims[0], self.dims[1], 3)) * 255
        self.frame = self.frame.astype('uint8')
        self.x_pixel = random.random()
        self.y_pixel = random.random()
        
        # image should belong to the same person
        self.target_path = './examples/target.jpg'
        self.source_path = './examples/source.jpg'
    
    def test_get_face_from_frame(self):
        results = face.get_face_from_frame(frame=self.frame, model_selection=0, min_detection_confidence=0.5)
        self.assertIsInstance(results, tuple)
        self.assertIsInstance(results[0], np.ndarray)
        self.assertIsInstance(results[1], np.ndarray)
    
    def test_verify(self):
        results = face.verify(self.target_path, self.source_path)
        self.assertIsInstance(results, dict)
        self.assertIsInstance(results['isIdentical'], bool)
        self.assertIsInstance(results['confidence'], float)
        self.assertTrue(results['isIdentical'])
    
    def test_normalized_to_pixel_coordinates(self):
        results = face.face_detection._normalized_to_pixel_coordinates(self.x_pixel, 
                                                                        self.y_pixel, 
                                                                        self.dims[0], 
                                                                        self.dims[1])
        self.assertIsInstance(results, tuple)
        self.assertIsInstance(results[0], int)
        self.assertIsInstance(results[1], int)
        
        self.assertGreaterEqual(results[0], 0)
        self.assertGreaterEqual(results[1], 0)
        self.assertLessEqual(results[0], self.dims[0])
        self.assertLessEqual(results[1], self.dims[1])