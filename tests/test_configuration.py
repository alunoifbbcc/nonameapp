import unittest
from app import create_app
from flask import current_app

class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')

    def tearDown(self):
        pass

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])
