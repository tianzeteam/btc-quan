# -*- coding: utf-8 -*-
import logging
import time
from flask import request, jsonify, g, current_app as app
from apps.utils import *
from decimal import Decimal
from apps.models import db, User, Flowlog,CommonSetting, Fangtang,BonusScene
from apps.common import identify_required, optional_identify_required, success_response
import config
from apps.utils import Utils
logger = logging.getLogger(__name__)


@optional_identify_required
def get_discount_tag():
    """ 平仓价是否会打折
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
            "data":{

                "discount": "YES| NO"

            }
        }
        ```
        @@@
        """
    user = g.user
    data = dict()
    data['discount'] = user.discount_tag

    return success_response(data=data)


@optional_identify_required
def get_prices():
    """ 取得价格信息(当前价格和开盘价格)
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

            "real_trade_price": "当前市场成交价格",
            "open_price":"开盘价格 0点价格"

        ]
    }
    ```
    @@@
    """
    setting = g.setting
    is_usdt = setting.is_usdt
    binance_client = g.binance_client
    data = {}
    symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
    real_trade_price = binance_client.get_recent_trades(symbol)
    today = str(datetime.date.today())
    open_price_key = today + '_' + symbol
    open_price = config.OPEN_PRICE_DATA.get(open_price_key)

    data['real_trade_price'] = str(real_trade_price)
    data['open_price'] = str(open_price)

    return success_response(data=data)