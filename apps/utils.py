#!/usr/bin/env python
# coding: utf-8

###############################################################
#   工具类
###############################################################

import time, datetime
import uuid
import logging
import traceback
from functools import wraps
import config

from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash


logger = logging.getLogger(__name__)


def parse_offset_limit(request):
    offset = int(request.args.get("offset") or 0)
    limit = int(request.args.get("limit") or 20)

    if offset < 0:
        offset = 0
    if limit < 5 or limit > 100:
        limit = 20
    if "page" in request.args or "size" in request.args:
        page = int(request.args.get('page') or 1)
        size = int(request.args.get('size') or 20)
        if page < 1:
            page = 1
        if size < 5 or size > 100:
            size = 20
        offset = (page - 1) * size
        limit = size
    return offset, limit


def response_wrapper(func):
    from apps import db
    @wraps(func)
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.error(traceback.format_exc())
            db.session.rollback()
            return jsonify({"code": "error", "info": "unknown error", "data": {}})
    return _inner


class Utils(object):

    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(hash, password):
        return check_password_hash(hash, password)

    def get_system_no(self):
        return str(uuid.uuid4()).replace('-', '')

    @staticmethod
    def time2second(to_hour):
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        str_time = str(today) + " " + str(to_hour) + ":" + "00" + ":" + "00"
        time_struct = time.strptime(str_time, '%Y-%m-%d %H:%M:%S')
        time_second = int(round(time.mktime(time_struct)*1000))
        return time_second

    def get_hour(self):
        return datetime.datetime.now().hour

    @staticmethod
    def get_open_price(symbol):
        today = str(datetime.date.today())
        open_price_key = today + '_' + symbol
        return config.OPEN_PRICE_DATA.get(open_price_key) if open_price_key in config.OPEN_PRICE_DATA else None

    @staticmethod
    def open_time():
        return int(time.mktime(datetime.date.today().timetuple()))*1000

    if __name__ == '__main__':
        from apps.utils import Utils
        print(Utils.get_open_price('BTCUSDT'))

