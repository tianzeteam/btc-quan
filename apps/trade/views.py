# -*- coding: utf-8 -*-

import time
import json
import logging
from apps.trade import tv
from .position import get_position_balance, immediate_close_position
from .order import get_all_orders, cancel_all_orders
from apps.common import identify_required
from apps.models import *

# create logger
logger = logging.getLogger(__name__)


tv.add_url_rule('/user/position', view_func=get_position_balance, methods=['GET'])
tv.add_url_rule('/user/position', view_func=immediate_close_position, methods=['DELETE'])
tv.add_url_rule('/user/orders', view_func=get_all_orders, methods=['GET'])

tv.add_url_rule('/user/orders', view_func=cancel_all_orders, methods=['DELETE'])

