# -*- coding: utf-8 -*-

import re
import time
import logging
import json

import urllib.parse
import urllib.request


from apps.utils import response_wrapper
from apps import db, tc_sms
from apps.user import uv

from .user import update_user, user_login, search_log, get_common_setting,update_common_setting,get_fangtang_setting,update_fangtang_setting,get_bonus_setting,update_bonus_setting,get_run_status,change_runstatus



from apps.common import *

logger = logging.getLogger()


@uv.route("/")
def hello():
    return jsonify({"message": "Hello, user!"})


uv.add_url_rule('/login', view_func=user_login, methods=['POST'])
uv.add_url_rule('/user/password', view_func=update_user, methods=['PUT'])
uv.add_url_rule('/user/logs', view_func=search_log, methods=['GET'])
uv.add_url_rule('/common/setting', view_func=get_common_setting, methods=['GET'])
uv.add_url_rule('/common/setting', view_func=update_common_setting, methods=['PUT'])

uv.add_url_rule('/fangtang/setting', view_func=get_fangtang_setting, methods=['GET'])
uv.add_url_rule('/fangtang/setting', view_func=update_fangtang_setting, methods=['PUT'])

uv.add_url_rule('/bonus/setting', view_func=get_bonus_setting, methods=['GET'])
uv.add_url_rule('/bonus/setting', view_func=update_bonus_setting, methods=['PUT'])

uv.add_url_rule('/user/runstatus', view_func=get_run_status, methods=['GET'])
uv.add_url_rule('/user/runstatus', view_func=change_runstatus, methods=['PUT'])
