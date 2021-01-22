# -*- coding: utf-8 -*-

import time
import datetime
import json
from apps import db
from apps.models import User

from apps.utils import Utils
from apps import redis_client
from decimal import Decimal
from apps import binance_client
from binance_f.base.printobject import *

from test.base import BaseCase


class TestBinanceClient(BaseCase):
    verify_info = {}
    user: User = None


    def hook_sender(self, phone, params, verify_type):
        self.verify_info = {"mobile": phone, "code": params[0], "minutes": params[1], "type": verify_type}
        return {"result": 0}

    def setUp(self):
        super().setUp()
        self.telephone = "18926157202"
        user = self.prepare_user(nickname=self.telephone)
        self.user_id = user.id
        self.user_headers = {"Authorization": "JWT " + user.access_token}


    def tearDown(self):
        # self.delete_tables([TelVerifyCode, User, Merchant,  BookSubject,  WithdrawBank, WithdrawApply, Enroll,Orders])
        # redis_client.remove_rank()
        pass

    def test_get_openprice_usdt(self):
        binance_client.get_open_price('BTCUSDT')

    def test_get_openprice_coin(self):
        binance_client.get_open_price('BTCUSD_PERP')

    def test_get_recent_trades_coin(self):
        price = binance_client.get_recent_trades('BTCUSD_PERP')
        print(price)

    def test_get_exchange_info_coin(self):
        binance_client.get_exchange_info_coin()

    def test_market_order_usdt(self):
        order_id, status = binance_client.market_order('BTCUSDT', 'SELL', Decimal(float(0.1)).quantize(Decimal('0.0000')))
        print('{}  {}'.format(order_id, status))

    def test_get_order_usdt(self):
        order_id, status = binance_client.market_order('BTCUSDT', 'SELL', Decimal(float(0.1)).quantize(Decimal('0.0000')))
        print('{}  {}'.format(order_id, status))
        avgPrice,status = binance_client.get_order('BTCUSDT', order_id)


    def test_market_order_coin(self):
        order_id, status = binance_client.market_order('BTCUSD_PERP', 'SELL', Decimal(2).quantize(Decimal('0.0000')))
        print('{}  {}'.format(order_id, status))

    def test_server_time(self):
        binance_client.get_server_time()
        print(int(round(time.time() * 1000)))

    def test_limit_order_usdt(self):
        print(round(19112.28, 2))
        result = binance_client.limit_order('BTCUSDT', 'BUY', 0.01, Decimal(19112.28).quantize(Decimal('0.00')))
        PrintBasic.print_obj(result)

    def test_limit_order_coin(self):
        result = binance_client.limit_order('BTCUSD_PERP','BUY', 3, 19850)
        PrintBasic.print_obj(result)

    def test_get_position_info_usdt(self):
        entryPrice ,positionAmt = binance_client.get_position_info('BTCUSDT')
        print((entryPrice,positionAmt))

    def test_get_position_info_coin(self):
        entryPrice ,positionAmt = binance_client.get_position_info('BTCUSD_PERP')
        print((entryPrice,positionAmt))

    def test_cancel_all_orders_usdt(self):
        result = binance_client.cancel_all_orders('BTCUSDT')
        val_str = str(getattr(result, 'code'))
        print('code' + ":" + val_str)

    def test_cancel_all_orders_coin(self):
        result = binance_client.cancel_all_orders('BTCUSD_PERP')
        val_str = str(getattr(result, 'code'))
        print('code' + ":" + val_str)

    def test_get_recent_trades(self):
        result = binance_client.get_recent_trades('BTCUSDT')
        print(result)

    def test_get_open_orders_usdt(self):
        result = binance_client.get_open_orders('BTCUSDT')
        PrintList.print_object_list(result)

    def test_get_open_orders_coin(self):
        result = binance_client.get_open_orders('BTCUSD_PERP')
        PrintList.print_object_list(result)

    def test_get_high_price_usdt(self):
        result = binance_client.get_high_price('BTCUSDT', 12)

