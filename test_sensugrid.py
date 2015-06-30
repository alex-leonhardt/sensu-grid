__author__ = 'ale'

import unittest
from sensugrid import app, Config

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


if __name__ == '__main__':
    unittest.main()
