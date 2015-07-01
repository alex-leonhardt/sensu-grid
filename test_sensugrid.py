__author__ = 'ale'

import os
import unittest
from sensugrid import app, Config
import coverage

class TestingConfig(Config):
    TESTING = True
    DEBUG = True


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client(use_cookies=True)

    def test_healthcheck(self):
        r = self.client.get('/healthcheck', content_type='application/json')
        self.assertEqual(r.status_code, 200)

    def test_root(self):
        r = self.client.get('/', content_type='text/html')
        self.assertEqual(r.status_code, 200)

    def test_detail(self):
        r = self.client.get('/vagrant', content_type='text/html')
        assert r.status_code < 399
        assert 'SENSU # GRID' in r.data
        assert '</html>' in r.data


if __name__ == '__main__':
    unittest.main()
