import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import unittest

import numpy as np

import face

class TestFace(unittest.TestCase):
    def setUp(self) -> None:
        self.dims = (640, 480)
        
        self.frame = np.random.random((self.dims[0], self.dims[1], 3)) * 255
        self.frame = self.frame.astype('uint8')
        
        # image should belong to the same person
        self.target_path = './examples/target.jpg'
        self.source_path = './examples/source.jpg'
    
    def test_get_face_from_frame(self):
        results = face.get_face_from_frame(frame=self.frame, model_selection=0, min_detection_confidence=0.5)
        self.assertEqual(type(results), tuple)
        self.assertEqual(type(results[0]), np.ndarray)
        self.assertEqual(type(results[1]), np.ndarray)
    
    def test_verify(self):
        results = face.verify(self.target_path, self.source_path)
        self.assertEqual(type(results), dict)
        self.assertEqual(type(results['isIdentical']), bool)
        self.assertEqual(type(results['confidence']), float)
        self.assertTrue(type(results['isIdentical']))