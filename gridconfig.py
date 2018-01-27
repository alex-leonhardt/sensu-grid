import os
import yaml


class Config(object):
    DEBUG = False
    TESTING = False

    with open(os.path.dirname(os.path.abspath(__file__)) + '/conf/config.yaml') as f:
        config = yaml.load(f)

    DCS = config['dcs']
    APPCFG = config['app']


class DevConfig(Config):
    DEBUG = True
    TESTING = False


class ProdConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
