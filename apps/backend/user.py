# coding:utf-8
"""
description: 后台管理-用户管理

"""
from flask import request
from apps.utils import *
from apps.models import User, db,CommonSetting,BonusScene,Fangtang
from apps.common import admin_identify_required, success_response, fail_response


@admin_identify_required
def search_user():
    """ 用户查询
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|
    |status    |true  |string | 用户状态 normal/del, 不传则标识全部 |
    |nickname |true   |string   |微信昵称|
    |offset   |true   |int   |偏移量|
    |limit   |true   |int   |每页限制|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":[
            'id': "",
            'nickname': "",
            "status": "",
            "create_time": ""
        ]
    }
    ```
    @@@
    """

    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 10)
    status = request.args.get('status')
    nickname = request.args.get('nickname')

    user_query = User.query
    if status:
        user_query = user_query.filter_by(status=status)
    if nickname:
        user_query = user_query.filter_by(nickname=nickname)

    user_count = user_query.count()
    user_query = user_query.offset(int(offset)).limit(int(limit))
    result = []
    for user in user_query:
        result.append({
            'id': user.id,
            'nickname': user.nickname,
            'status': user.status,
            'create_time': user.create_time
        })
    return success_response('', result, total=user_count)


@admin_identify_required
def block_user(user_id):
    """ 封禁用户
    :param user_id:  user_id
    @@@
    ### return
    ```json
    {
        "code": "success/error",
        "info": "",
        "data": {}
    }
    ```
    @@@
    """
    user = User.query.filter_by(id=user_id, status='normal').first()
    if not user:
        return fail_response('用户不存在或已被封禁')
    user.status = 'del'
    db.session.commit()
    return success_response()


@admin_identify_required
def change_password():
    """ 修改用户密码
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|
    |user_id    |false  |int | 用户状态id |
    |password |false   |int   |用户密码|

    ### return
    ```json
    {
        "code": "success/error",
        "info": "",
        "data": {}
    }
    ```
    @@@
    """
    json_data = request.json or {}
    user_id = json_data.get('user_id')
    password = json_data.get('password', None)
    user = User.query.filter_by(id=int(user_id), status='normal').first()
    if not password:
        return fail_response('密码不能为空')
    if not user:
        return fail_response('用户不存在或已被封禁')
    user.password = Utils.set_password(password)
    db.session.commit()
    return success_response()


def add_user():
    """ 新增用户
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
            "user_id": 管理员 id,
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
        return fail_response('empty field')
    au = User.query.filter_by(nickname=nickname).first()
    if au:
        return fail_response('user is exist')
    try:
        user = User(nickname=nickname, password=Utils.set_password(password), discount_tag='NO',status='normal')

        db.session.add(user)
        db.session.flush()

        setting = CommonSetting(user_id=user.id)
        fangtang = Fangtang(user_id=user.id)
        bonus_scene = BonusScene(user_id=user.id)
        db.session.add(setting)
        db.session.add(fangtang)
        db.session.add(bonus_scene)
        db.session.commit()
    except:
        db.session.rollback()
    return success_response()


