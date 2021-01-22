# -*- coding: utf-8 -*-


from binance_f.constant.test import *
from binance_f.base.printobject import PrintList,PrintBasic
from binance_f.model.constant import *
from binance_f import RequestClient as UsdtClient


from binance_d.model import *
from binance_d.constant.test import *
from binance_d.base.printobject import *
from binance_d import RequestClient as CoinClient

from traceback import print_exc
from apps.utils import Utils
import logging


logger = logging.getLogger()


class BinanceUserApi:
    def __init__(self, app, user):
        self.binance_client_usdt = UsdtClient(api_key=user.api_key,
                                                    secret_key=user.api_secret,
                                                    url=app.config['BASE_REST_API_URL'])
        self.binance_client_coin = CoinClient(api_key=user.api_key,
                                                    secret_key=user.api_secret,
                                                    url=app.config['BASE_REST_API_URL'])

    # 截止指定时间合约最高价格
    def get_high_price(self, symbol, to_hour):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin

        start_time = Utils.open_time()
        end_time = Utils.time2second(to_hour)
        result = binance_client_api.get_candlestick_data(symbol=symbol, interval=CandlestickInterval.MIN30,
                                                         startTime=start_time, endTime=end_time, limit=100)
        high_price_list = [getattr(x, 'high') for x in result]
        return max(high_price_list)

    # 市场价开仓 平仓
    def market_order(self, symbol, side, quantity):

        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        try:
            result = binance_client_api.post_order(symbol=symbol, side=side, ordertype=OrderType.MARKET,
                                                   quantity=float(quantity))
            order_id = getattr(result, 'orderId')
            status = getattr(result, 'status')
            return order_id, status
        except:
            return None, None

    # 取得所有限价挂单
    def get_open_orders(self, symbol):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        result = binance_client_api.get_open_orders(symbol=symbol)
        return result

    # 合约 限价单挂单
    def limit_order(self, symbol, side, quantity, price):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        result = binance_client_api.post_order(symbol=symbol, side=side, price=price, ordertype=OrderType.LIMIT,
                                               timeInForce='GTC', quantity=quantity)
        return result

    # 持仓信息(持仓数量 持仓均价)
    def get_position_info(self, symbol):
        if symbol == 'BTCUSDT':
            usdt_list = self.binance_client_usdt.get_position_v2(symbol)
        else:
            coin_list = self.binance_client_coin.get_position(symbol)
            for x in coin_list:
                x_symbol = getattr(x, 'symbol')
                if x_symbol == symbol:
                    return float(getattr(x, 'entryPrice')), float(getattr(x, 'positionAmt'))
        return float(getattr(usdt_list[0], 'entryPrice')), float(getattr(usdt_list[0], 'positionAmt'))

    # 撤销合约所有挂单
    def cancel_all_orders(self, symbol):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        result = binance_client_api.cancel_all_orders(symbol=symbol)
        return result

    def get_server_time(self):
        result = self.binance_client_usdt.get_servertime()

        print("server time: ", result)

    # 合约开盘价（0点价格）
    def get_open_price(self, symbol):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        start_time = Utils.open_time()
        result = binance_client_api.get_candlestick_data(symbol=symbol, interval=CandlestickInterval.MIN1,
                                                         startTime=start_time, limit=10)

        val_str = getattr(result[0], 'open')
        return float(val_str)

    #  合约最新价格
    def get_recent_trades(self, symbol):
        binance_client_api = self.binance_client_usdt if symbol == 'BTCUSDT' else self.binance_client_coin
        result = binance_client_api.get_recent_trades_list(symbol=symbol, limit=10)
        result.reverse()
        for recent_trade in result:
            price = getattr(recent_trade, 'price')
            is_buyer_maker = getattr(recent_trade, 'isBuyerMaker')
            if is_buyer_maker:
                return float(price)
        return float(price)

    # 获取coin本位交易对信息
    def get_exchange_info_coin(self):
        result = self.binance_client_coin.get_exchange_information()

        print("======= exchange info  Data =======")

        print("serverTime: ", result.serverTime)
        print("===================")
        print("=== Symbols ===")
        PrintMix.print_data(result.symbols)


