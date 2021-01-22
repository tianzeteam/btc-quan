# -*- coding: utf-8 -*-

import time
import datetime

import jwt
from flask import jsonify

from apps import db
from apps.models import User, AdminUser


class Auth(object):

    @staticmethod
    def encode_auth_token(user_id, login_time, timedelta, SECRET_KEY):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + timedelta,
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token, SECRET_KEY):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            # 取消过期时间验证
            # payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': False})
            if 'data' in payload and 'id' in payload['data']:
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise jwt.ExpiredSignatureError

    def authenticate(self, user, timedelta, SECRET_KEY):
        """
        用户登录，登录成功返回token和用户id，写将登录时间写入数据库；登录失败返回失败原因
        :param telephone:
        :param verify_code:
        :return: json
        """
        login_time = int(time.time())

        token = self.encode_auth_token(user.id, login_time, timedelta, SECRET_KEY)
        print(token)
        token = token.decode()

        user.login_time = login_time
        user.access_token = token
        db.session.commit()
        data = dict()
        data['code'] = 'success'
        data['data'] = {"u_token": token, 'user_id': user.id, 'nickname': user.nickname}
        return jsonify(data)

    def authenticate_admin_user(self, admin_user, timedelta, SECRET_KEY):
        """
        后台管理员登录
        :param admin_user:
        :param timedelta:
        :param SECRET_KEY:
        :return:
        """
        login_time = int(time.time())
        token = self.encode_auth_token(admin_user.id, login_time, timedelta, SECRET_KEY)
        token = token.decode()
        admin_user.login_time = login_time
        admin_user.access_token = token
        db.session.commit()
        data = dict()
        data['code'] = 'success'
        data['data'] = {"a_token": token, 'admin_user_id': admin_user.id, 'nickname': admin_user.nickname}
        return jsonify(data)

    def identify(self, auth_header, SECRET_KEY):
        """
         后台用户鉴权
       """
        data = dict()
        data['code'] = 'error'
        if auth_header:
            auth_token_arr = auth_header.split(" ")
            if not auth_token_arr or auth_token_arr[0] != 'JWT' or len(auth_token_arr) != 2:
                data['info'] = "请传递正确的验证头信息"
            else:
                try:
                    auth_token = auth_token_arr[1]
                    payload = self.decode_auth_token(auth_token, SECRET_KEY)
                except:
                    data['info'] = "Token失效"
                    return data
                if not isinstance(payload, str):
                    user_id = payload['data']['id']
                    user = User.query.filter(User.id == user_id).first()
                    if not user:
                        data['info'] = "当前用户不存在"
                    else:
                        if user.login_time == payload['data']['login_time']:
                            data['code'] = "success"
                            data['user_id'] = user.id
                            data["data"] = user
                        else:
                            data['info'] = "非法访问请求"
                else:
                    return payload
        else:
            data['info'] = "没有提供认证token"
        return data

    @staticmethod
    def admin_identify(auth_header, SECRET_KEY):
        """
        后台用户鉴权
        :param auth_header: Request header `Authorization`
        :param SECRET_KEY:
        :return: {"code": "success/error", "info": "", "data": ""/{}}
        """
        data = {"code": "error"}
        if not auth_header:
            data['info'] = "没有提供认证token"
            return data
        auth_tokens = auth_header.split(" ")
        if (not auth_tokens) or (auth_tokens[0] != 'JWT') or (len(auth_tokens) != 2):
            data['info'] = "请传递正确的验证头信息"
            return data
        auth_token = auth_tokens[1]
        try:
            payload = Auth.decode_auth_token(auth_token, SECRET_KEY)
        except:
            data['info'] = "Token失效"
            return data
        if isinstance(payload, str):
            data.update({
                "code": "success",
                "data": payload,
            })
            return data
        admin_id = payload['data']['id']
        admin = AdminUser.query.filter_by(id=admin_id).first()
        if (not admin) or (admin.login_time != payload['data']['login_time']):
            data['info'] = "非法访问请求"
            return data
        data.update({
            "code": "success",
            "data": admin,
        })
        return data


