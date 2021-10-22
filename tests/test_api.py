import sys
from os.path import abspath, dirname, join
sys.path.insert(1, abspath(join(dirname(dirname(__file__)), 'src')))

import unittest

from fastapi.testclient import TestClient

from api import app

class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
    
    def test_root(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

