# -*- coding: utf-8 -*-

import logging
import redis
import json
from traceback import print_exc


logger = logging.getLogger()


class RedisClient:
    def __init__(self):
        self.pool = ""
        self.redis_client = ""
        self.MY_ASSIST_RANK = 'MY_ASSIST_RANK'

    def init_from_app(self, app):
        self.redis_client = redis.Redis(host=app.config['REDIS_SERVER_HOST'], port=6379, db=0)
