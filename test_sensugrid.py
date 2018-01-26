import os
import unittest
from sensugrid import app
from griddata import *
from gridconfig import TestingConfig
import coverage

__author__ = 'ale'
myconfig = TestingConfig


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config.from_object(myconfig)
        self.client = self.app.test_client(use_cookies=True)

    def test_healthcheck(self):
        r = self.client.get('/healthcheck', content_type='application/json')
        assert r.status_code < 400

    def test_root(self):
        r = self.client.get('/', content_type='text/html')
        assert r.status_code < 400

    def test_detail(self):
        r = self.client.get('/show/vagrant', content_type='text/html')
        assert r.status_code < 400
        assert 'SENSU # GRID' in r.data
        assert '</html>' in r.data

    def test_filtered_root(self):
        r = self.client.get('/filtered/test', content_type='text/html')
        assert r.status_code < 400
        assert 'SENSU # GRID' in r.data
        assert '</html>' in r.data


if __name__ == '__main__':
    unittest.main()
