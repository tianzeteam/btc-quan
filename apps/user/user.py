# -*- coding: utf-8 -*-
import logging
import time
from flask import request, g, current_app
from apps.utils import *
from apps.core.HandlePipes import HandlePipes
from apps.models import db, User, Flowlog, CommonSetting, Fangtang, BonusScene, RunStatus
from apps.common import identify_required, success_response, async_func
from apps.auths import Auth
from apps.utils import Utils

auth = Auth()

logger = logging.getLogger(__name__)


@identify_required
def get_run_status():
    """取得运行状态
       @@@
       #### data

       | args | nullable | type | remark |
       |--------|--------|--------|--------|



       #### return
       - ##### 成功 json
           ```
            {"code": "success",
                "data": {
                    "status": "active,ready,stop"
                }
            }
        ```
       """

    user_id = g.user_id
    data = {}

    run_status = RunStatus.query.filter_by(user_id=user_id).first()
    if run_status:
        data['status'] = run_status.status
    else:
        run_status = RunStatus(user_id=user_id, status='stop')
        db.session.add(run_status)
        db.session.commit()
        data['status'] = 'stop'

    return success_response(data=data)


@identify_required
def change_runstatus():
    """变更运行状态
    @@@
    #### data

    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    curr_status    |    false    |    string   | 当前状态（ready ,stop,active)   |


    #### return
    - ##### 成功 json
    > {"code": "success"}
    """
    json_data = request.json or {}
    user = g.user

    curr_status = json_data.get("curr_status", None)

    working_app = current_app._get_current_object()

    run_status = RunStatus.query.filter_by(user_id=user.id).first()

    if run_status:
        if curr_status == 'ready':
            quan_pipe = HandlePipes()
            quan_pipe.run(working_app,  user.id)
        elif curr_status == 'stop':
            run_status.status = 'ready'
            db.session.commit()
        else:
            run_status.status = 'stop'
            db.session.commit()

    return jsonify({"code": "success"})


@identify_required
def update_user():
    """修改用户密码
    @@@
    #### data

    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    password    |    true    |    string   | 密码   |


    #### return
    - ##### 成功 json
    > {"code": "success"}
    """
    json_data = request.json or {}
    user_id = g.user_id

    password = json_data.get("password", None)

    user = User.query.filter_by(id=user_id).first()
    if user and password:
        user.password = Utils.set_password(password)
        db.session.commit()
    return jsonify({"code": "success"})


@identify_required
def get_user():
    """用户得到自己的资料
    @@@

    #### return
    - ##### 成功 json
    ```
    {"code": "success",
        "data": {
            "id": 1,
            "nickname": "xxx"
        }
    }
    ```
    """
    user = g.user
    data = {
        "id": user.id,
        "nickname": user.nickname
    }
    return jsonify({"code": "success", "data": data})


def user_login():
    """ 用户登录
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
            "u_token": token,
            "user_id": 用户id,
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
    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        return jsonify({"code": "error", "info": "no such user"})
    if not Utils.check_password(user.password, password):
        return jsonify({"code": "error", "info": "password error"})
    return auth.authenticate(user, current_app.config['USER_TOKEN_USEFUL_DATE'], current_app.config['SECRET_KEY'])


@identify_required
def get_common_setting():
    """ 取得常规设置信息
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":[
            'id': "",
            'user_id': "",
            "once_amount": "",
            "close_difference":"",
            "amount_of_market_price": "",
            .............

        ]
    }
    ```
    @@@
    """
    user_id = g.user_id

    setting = CommonSetting.query.filter(CommonSetting.user_id == user_id).first()
    data = setting.as_dict() if setting else None
    return success_response(data=data)


@identify_required
def update_common_setting():
    """ 常规设置编辑
        @@@
        ### args
        |args           |nullable|type  |remark     |
        |---------------|--------|------|-----------|
        |once_amount   |false   |int   |单次数量|
        |close_difference   |false   |int   |平仓差价|
        |amount_of_market_price   |false   |int   |市价总量 |
        |difference_of_market_price   |false   |int   | 市价差价|
        |list_difference_of_limit_price   |false   |list   | 限价差价数组|
        |list_difference_of_limit_amount  |false   |list   | 限价数量数组|
        |dynamic_1_price   |false   |int   |动态价格1点百分比 |
        |difference_dynamic_1_price   |false   |int   | 动态价格1点价差|
        |dynamic_2_price   |false   |int   | 动态价格2点百分比|
        |difference_dynamic_2_price   |false   |int   |动态价格点2价差 |
        |is_limit_price   |false   |string   |是否添加限价单 |
        |is_usdt   |false   |string   | 是U本位 or COIN 本位|
        |is_long   |false   |string   | 是否做多|
        |price_interval_time   |false   |int   | 当前价格查询间隔时间|
        |wait_interval_update_time   |false   |int   |刷新价格等待间隔时间 |
        |auto_start_time   |false   |int   | 自动调整平仓时间|
        |auto_close_price_per   |false   |int   | 自动平仓价格百分比|

        ### return
        - #### json
        ```json
        {
            "code": "success/error",
            "info": ""
        }
        ```
        @@@
        """
    user_id = g.user_id
    json_data = request.json or {}
    setting = CommonSetting.query.filter(CommonSetting.user_id == user_id).first()

    for field in ("once_amount", "close_difference", "amount_of_market_price", "difference_of_market_price",
                  "list_difference_of_limit_price", "list_difference_of_limit_amount", "dynamic_1_price",
                  "difference_dynamic_1_price", "dynamic_2_price", "difference_dynamic_2_price","is_limit_price",
                  "is_usdt", "is_long", "price_interval_time","wait_interval_update_time","auto_start_time",
                  "auto_close_price_per"):
        if field in json_data:
            setattr(setting, field, json_data[field])
    db.session.commit()
    return success_response()


@identify_required
def get_fangtang_setting():
    """ 取得方糖设置信息
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":[
            'id': "",
            'user_id': "",
            "title": "",
            "api_key":"",
            "api_secret": "",
            "ft_key": ""

        ]
    }
    ```
    @@@
    """
    user = g.user
    data = {}

    setting = Fangtang.query.filter(Fangtang.user_id == user.id).first()

    if setting:
        data['title'] = setting.title
        data['ft_key'] = setting.ft_key
    data['api_key'] = user.api_key
    data['api_secret'] = user.api_secret

    return success_response(data)


@identify_required
def update_fangtang_setting():
    """ 方糖设置编辑
        @@@
        ### args
        |args           |nullable|type  |remark     |
        |---------------|--------|------|-----------|
        |title   |true   |string   |方糖通知标题|
        |ft_key   |true   |string   |方糖通知key|
        |api_key   |true   |string   |币安接口key|
        |api_secret   |true   |string   | 币安接口密钥|



        ### return
        - #### json
        ```json
        {
            "code": "success/error",
            "info": ""
        }
        ```
        @@@
        """
    user_id = g.user_id
    json_data = request.json or {}
    setting = Fangtang.query.filter(Fangtang.user_id == user_id).first()
    user = User.query.filter(User.id == user_id).first()
    try:
        for field in ("title", "ft_key"):
            if field in json_data:
                setattr(setting, field, json_data[field])
        for field in ("api_key", "api_secret"):
            if field in json_data:
                setattr(user, field, json_data[field])
        db.session.commit()
    except:
        db.session.rollback()
    return success_response()


@identify_required
def get_bonus_setting():
    """ 取得彩蛋信息
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":[
            'id': "",
            'user_id': "",
            "start_time": "",
            "end_time":"",
            "bonus_diff": "",
            "bonus_amount": ""

        ]
    }
    ```
    @@@
    """
    user = g.user
    data = {}

    setting = BonusScene.query.filter(BonusScene.user_id == user.id).first()

    if setting:
        data['start_time'] = setting.start_time
        data['end_time'] = setting.end_time
        data['bonus_diff'] = setting.bonus_diff
        data['bonus_amount'] = setting.bonus_amount

    return success_response(data=data)


@identify_required
def update_bonus_setting():
    """ 彩蛋设置编辑
        @@@
        ### args
        |args           |nullable|type  |remark     |
        |---------------|--------|------|-----------|
        |start_time   |false   |int   |起始时间|
        |end_time     |false   |int   |截止时间|
        |bonus_diff   |true    |int   |彩蛋差价|
        |bonus_amount |true    |float | 彩蛋数量|



        ### return
        - #### json
        ```json
        {
            "code": "success/error",
            "info": ""
        }
        ```
        @@@
        """
    user_id = g.user_id
    json_data = request.json or {}
    setting = BonusScene.query.filter(BonusScene.user_id == user_id).first()

    for field in ("start_time", "end_time", "bonus_diff", "bonus_amount"):
        if field in json_data:
            setattr(setting, field, json_data[field])
    db.session.commit()
    return success_response()


@identify_required
def search_log():
    """ 日志内容查询
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|
    |offset   |true   |int   |偏移量|
    |limit   |true   |int   |每页限制|
    |sort   |false   |string   |[desc asc]倒序 or 顺序|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "",
        "data":[
            'id': "",
            'user_id': "",
            "content": "",
            "log_type":"",
            "create_time": ""
        ]
    }
    ```
    @@@
    """
    user_id = g.user_id
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 10)
    sort = request.args.get('sort', 'desc')

    log_query = Flowlog.query

    log_count = log_query.filter(Flowlog.user_id == user_id).count()

    if sort == 'desc':
        log_list = log_query.filter(Flowlog.user_id == user_id) \
                .order_by(Flowlog.create_time.desc()) \
                .offset(int(offset))\
                .limit(int(limit))
    else:
        log_list = log_query.filter(Flowlog.user_id == user_id) \
                 .order_by(Flowlog.create_time.desc()) \
                 .offset(int(offset))\
                 .limit(int(limit))
    result = []
    for log in log_list:
        result.append({
            'id': log.id,
            'content': log.content,
            'log_type': log.log_type,
            'create_time': log.create_time
        })
    return success_response('', result, total=log_count)


