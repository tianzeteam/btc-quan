# -*- coding: utf-8 -*-

import json
import logging
import time
from functools import wraps
from traceback import print_exc

from flask import request, current_app, jsonify, g
from .binance_client import BinanceClient
from threading import Thread

from apps.auths import Auth
from apps.models import User,  AdminUser, CommonSetting,db
from flask import jsonify, Response
from apps.binance_user_api import BinanceUserApi

logger = logging.getLogger(__name__)


def async_func(func):
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def iterate_user_func(func):
    @wraps(func)
    def decorated_function(bind_db,app,user):
        page = 1
        limit = 20
        while True:
            offset = (page - 1) * limit
            user_list = User.query.filter(User.status == 'normal').limit(limit).offset(offset)
            try:
                if user_list.first():
                    for user in user_list:
                        try:
                            func(bind_db=bind_db,app=app, user=user)
                        except:
                            print_exc(limit=10)
                    page += 1
                else:
                    print('SETTLE ----JUMP ')
                    break
            except:
                db.session.close()
                print_exc(limit=10)
        return None
    return decorated_function


def access_token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        working_app = current_app._get_current_object()
        data = Auth.identify(Auth, auth_header, working_app.config['SECRET_KEY'])
        if (not data) or data['code'] == "error":
            return jsonify(data)
        return func(*args, **kwargs)
    return decorated_function


def identify_required(func):
    func.__doc__ = (func.__doc__ or "").replace("@@@", "@@@\n### permission\nUser(用户权限)", 1)

    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        print('auth_header ', auth_header)
        working_app = current_app._get_current_object()
        data = Auth.identify(Auth, auth_header, working_app.config['SECRET_KEY'])
        logger.info(data)
        try:
            if 'user_id' in data:
                g.user_id = data['user_id']
                g.user: User = data["data"]
            else:
                return jsonify(data)
        except:
            print_exc(limit=3)
        return func(*args, **kwargs)
    return decorated_function


def optional_identify_required(func):
    func.__doc__ = (func.__doc__ or "").replace("@@@", "@@@\n### permission\nOptional User(访问交易所接口权限)", 1)

    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        working_app = current_app._get_current_object()
        data = Auth.identify(Auth, auth_header, working_app.config['SECRET_KEY'])
        logger.info(data)
        try:
            if 'user_id' in data:
                g.user_id = data['user_id']
                g.user: User = data["data"]
                api_key = g.user.api_key
                api_secret = g.user.api_secret
                if not api_key or not api_secret:
                    data['info'] = 'no set api key or api secret'
                    return jsonify(data)
                g.binance_client: BinanceUserApi = BinanceUserApi(working_app, g.user)
                #g.setting: CommonSetting = CommonSetting.query.filter(CommonSetting.user_id == data['user_id']).first()
            else:
                return jsonify(data)
        except:
            print_exc(limit=3)
        return func(*args, **kwargs)
    return decorated_function


def admin_identify_required(func):
    func.__doc__ = (func.__doc__ or "").replace("@@@", "@@@\n### permission\nAdmin(管理员权限)", 1)

    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        working_app = current_app._get_current_object()
        data = Auth.admin_identify(auth_header, working_app.config['SECRET_KEY'])
        if (not data) or data['code'] == "error":
            return jsonify(data)
        g.admin: AdminUser = data["data"]
        return func(*args, **kwargs)
    return decorated_function


def response(code: str, info: str, data: dict, **extra) -> Response:
    """
    基础返回
    :param code:    响应码
    :param info:    响应信息
    :param data:    响应数据
    :return:
    """
    ret = {'code': code, 'info': info, 'data': data}
    ret.update(extra)
    return jsonify(ret)


def success_response(info: str = '', data=None, **extra) -> Response:
    """
    成功返回
    :param info:
    :param data:
    :return:
    """
    if data is None:
        data = {}
    return response('success', info, data, **extra)


def fail_response(info: str, data=None, **extra) -> Response:
    """
    失败返回
    :param info:
    :param data:
    :return:
    """
    if data is None:
        data = {}
    return response('error', info, data, **extra)



