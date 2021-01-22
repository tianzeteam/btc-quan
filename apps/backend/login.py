# -*- coding: utf-8 -*-
import json
from flask import request, jsonify, g, current_app as app

from apps.auths import Auth
from apps.models import AdminUser
from apps.utils import response_wrapper, Utils

auth = Auth()


def login():
    """ 管理员登录
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|
    |nickname          |false  |string|用户名|
    |password           |false  |string|密码|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":{
            "a_token": token,
            "admin_user_id": 管理员 id,
            "nickname": 昵称
        }
    }
    ```
    @@@
    """
    json_data = request.json or {}
    nickname = json_data.get("nickname")
    password = json_data.get("password")
    if (not nickname) or (not password):
        return jsonify({"code": "error", "info": "empty field"})
    au = AdminUser.query.filter_by(nickname=nickname).first()
    if not au:
        return jsonify({"code": "error", "info": "no such admin"})
    if not Utils.check_password(au.password, password):
        return jsonify({"code": "error", "info": "password error"})
    return auth.authenticate_admin_user(au, app.config['USER_TOKEN_USEFUL_DATE'], app.config['SECRET_KEY'])
