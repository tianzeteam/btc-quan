# -*- coding: utf-8 -*-

import os
import datetime
import tempfile

basedir = os.path.abspath(os.path.dirname(__file__))
database_uri = os.environ.get('TEST_DATABASE_URL')

# 进程间通讯设置

MANAGER_PORT = 6000
MANAGER_DOMAIN = '0.0.0.0'
MANAGER_AUTH_KEY = 'binancewsflaskinter'

MARKET_PRICE = 18900
OPEN_PRICE_DATA = {}


class Config:
    API_DOC_MEMBER = ["core", "api", "platform"]  # 需要显示文档的 Api
    RESTFUL_API_DOC_EXCLUDE = []  # 需要排除的 RESTful Api 文档
    JSON_AS_ASCII = False
    # secret_key setting
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    # database setting
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_POOL_TIMEOUT = 5
    SQLALCHEMY_ECHO = False

    # Token
    ADMIN_TOKEN_USEFUL_DATE = datetime.timedelta(days=7)
    USER_TOKEN_USEFUL_DATE = datetime.timedelta(days=7)

    # scheduler setting
    USER_PAGE_LIMIT = 20

    # tencent sms setting
    SMS_APP_ID = 'xxx020xxx08'
    SMS_APP_KEY = '873d9xxxxx9ba3ac38eb2xxxxe985bd7d3'


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mhm@123456@127.0.0.1:3306/btcbot-dev'
    CDN_STATIC_PATH = tempfile.gettempdir()
    CDN_STATIC_URL = 'http://cdn.liyun.com/static/'
    REDIS_SERVER_HOST = '127.0.0.1'
    BASE_REST_API_URL = 'https://testnet.binancefuture.com'
    WS_STREAM_URI = 'wss://sdstream.binancefuture.com/ws'
    BINANCE_API_KEY = '06a9e4f9b350215c492e81032cf6b4302da8882d2eb66422b65a24a91c9446a2'
    BINANCE_API_SECRET = '3ee38ffce75ee2be4760b396f7b418e270b1840f8e33b7ce145e7e836f77c172'


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mhm@123456@127.0.0.1:3306/btcbot-dev'
    CDN_STATIC_PATH = tempfile.gettempdir()
    CDN_STATIC_URL = 'http://cdn.liyun.com/static/'
    REDIS_SERVER_HOST = '127.0.0.1'
    BASE_REST_API_URL = 'https://testnet.binancefuture.com'
    WS_STREAM_URI = 'wss://sdstream.binancefuture.com/ws'
    BINANCE_API_KEY = '06a9e4f9b350215c492e81032cf6b4302da8882d2eb66422b65a24a91c9446a2'
    BINANCE_API_SECRET = '3ee38ffce75ee2be4760b396f7b418e270b1840f8e33b7ce145e7e836f77c172'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mhm@123456@127.0.0.1:3306/btcbot-dev'
    CDN_STATIC_PATH = '/usr/local/www/static/'
    CDN_STATIC_URL = 'http://cdn.liyun.com/static/'
    REDIS_SERVER_HOST = '127.0.0.1'
    BASE_REST_API_URL = 'https://dapi.binance.com'
    WS_STREAM_URI = 'wss://dstream.binance.com/ws'
    BINANCE_API_KEY = 'fcc8c9906d82f1246838544049f147acc1a0deb780a223f6554558ef35d8ea32'
    BINANCE_API_SECRET = '7b38d654dd0cde83ab111a6f0074e0b4b25e2bd60595842f798159561359a82a'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
