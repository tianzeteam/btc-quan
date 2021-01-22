# -*- coding: utf-8 -*-
import logging
import time
from flask import request, jsonify, g, current_app as app
from apps.utils import *
from decimal import Decimal
from apps.models import db, User, Flowlog,CommonSetting, Fangtang,BonusScene
from apps.common import identify_required, optional_identify_required, success_response, fail_response
from apps.auths import Auth
from apps.utils import Utils
logger = logging.getLogger(__name__)


@optional_identify_required
def get_all_orders():
    """ 取得所有挂单
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
            "limit_price":"挂单价格",
            "symbol": "货币对",
            "amount": "数量"

        ]
    }
    ```
    @@@
    """
    setting = g.setting
    is_usdt = setting.is_usdt
    binance_client = g.binance_client
    symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'

    order_list = binance_client.get_open_orders(symbol)
    data = [{'limit_price': x.price, 'symbol': x.symbol, 'amount': x.origQty} for x in order_list]

    return success_response(data=data)


@optional_identify_required
def cancel_all_orders():
    """ 取消所有挂单
    @@@
    ### args
    |args           |nullable|type  |remark     |
    |---------------|--------|------|-----------|

    ### return
    - #### json
    ```json
    {
        "code": "success/error",
        "info": "The operation of cancel all open order is done."
    }
    ```
    @@@
    """
    setting = g.setting
    is_usdt = setting.is_usdt
    binance_client = g.binance_client
    symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'

    result = binance_client.cancel_all_orders(symbol=symbol)
    code = getattr(result, 'code')
    info = getattr(result, 'msg')

    if code == 200:
        return success_response(info=info)
    else:
        return fail_response(info=info)