# -*- coding: utf-8 -*-
import logging
import time
from flask import g, current_app
from apps.utils import *
from decimal import Decimal
from apps.models import db, User, Flowlog,CommonSetting, Fangtang,BonusScene,Position
from apps.common import async_func, optional_identify_required, success_response
from sqlalchemy import *
logger = logging.getLogger(__name__)


@async_func
def roll_update_price(app, binance_client, user_id, update_price, symbol):
    with app.app_context():
        setting = CommonSetting.query.filter(CommonSetting.user_id == user_id).first()
        wait_interval_update_time = setting.wait_interval_update_time
        time.sleep(wait_interval_update_time)
        entry_price, quantity = binance_client.get_position_info(symbol=symbol)
        is_long = setting.is_long
        next_update_price = binance_client.get_recent_trades(symbol=symbol)

        if is_long == 'LONG':
            if float(next_update_price) < float(update_price):
                binance_client.market_order(symbol, 'SELL', Decimal(abs(quantity)).quantize(Decimal('0.0000')))
                return
            else:
                roll_update_price(app, binance_client, user_id, next_update_price, symbol)
        else:
            print('next_update_price:{}   update_price{}'.format(next_update_price,update_price))
            if float(next_update_price) > float(update_price):
                binance_client.market_order(symbol, 'BUY', Decimal(abs(quantity)).quantize(Decimal('0.0000')))
                return
            else:
                roll_update_price(app, binance_client, user_id, next_update_price, symbol)


@optional_identify_required
def immediate_close_position():
    """ 立即平仓
        @@@
        ### args
        |args           |nullable|type  |remark     |
        |---------------|--------|------|-----------|

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
    user = g.user
    setting = g.setting
    is_usdt = setting.is_usdt
    working_app = current_app._get_current_object()
    binance_client = g.binance_client
    symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
    update_price = binance_client.get_recent_trades(symbol=symbol)
    roll_update_price(working_app, binance_client, user.id, update_price, symbol)
    return success_response()


@optional_identify_required
def get_position_balance():
    """ 取得仓位与盈亏信息
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
            "entryPrice": "持仓均价",
            "positionAmt":"持仓数量",
            "symbol": "货币对",
            "diffPrice": "盈亏价差"，
            "profitAmt": "盈亏金额",
            "is_usdt": "u本位还是币本位",
            "is_long": "做多还是做空"

        ]
    }
    ```
    @@@
    """
    setting = g.setting
    user = g.user
    is_usdt = setting.is_usdt
    is_long = setting.is_long
    binance_client = g.binance_client
    symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
    wait_interval_update_time = setting.wait_interval_update_time
    print('wait_interval_update_time ', wait_interval_update_time)

    data = {}
    position = Position.query.filter(and_(Position.user_id == user.id, Position.symbol == symbol)).first()

    entry_price = position.entry_price if position else '0.00'
    position_amt = position.position_amount if position else '0.00'
    data['entryPrice'] = str(entry_price)
    data['positionAmt'] = str(position_amt)
    data['is_usdt'] = is_usdt
    data['is_long'] = is_long
    if is_usdt and is_long:
        recent_trade_price = binance_client.get_recent_trades(symbol=symbol)
        if is_long == 'LONG':
            diff_price = (Decimal(recent_trade_price) - Decimal(entry_price)).quantize(Decimal('0.00'))
            profit_amt = ((Decimal(recent_trade_price) - Decimal(entry_price))*Decimal(position_amt)).quantize(Decimal('0.00'))
        else:
            diff_price = (Decimal(entry_price)-Decimal(recent_trade_price)).quantize(Decimal('0.00'))
            profit_amt = ((Decimal(entry_price)-Decimal(recent_trade_price))*Decimal(abs(position_amt))).quantize(Decimal('0.00'))
        data['diffPrice'] = str(diff_price) if float(position_amt) > 0 or float(position_amt) < 0 else '0.00'
        data['profitAmt'] = str(profit_amt)
        data['recent_trade_price'] = str(recent_trade_price)
    else:
        pass

    return success_response(data=data)