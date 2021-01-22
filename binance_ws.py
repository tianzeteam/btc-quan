import logging
from binance_f import SubscriptionClient
from binance_f.constant.test import *
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException

from binance_f.base.printobject import *

from apps import create_app
import config
from process_communication import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
print(os.getenv('FLASK_CONFIG'))

logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

manager_server = ManagerServer(config.MANAGER_DOMAIN, config.MANAGER_PORT, config.MANAGER_AUTH_KEY)


def share_communication_start():
    manager_server.run()


sub_client = SubscriptionClient(api_key=app.config['BINANCE_API_KEY'], secret_key=app.config['BINANCE_API_SECRET'],
                                uri=app.config['WS_STREAM_URI'])


def callback(data_type: 'SubscribeMessageType', event: 'any'):
    if data_type == SubscribeMessageType.RESPONSE:
        print("Event ID: ", event)
    elif data_type == SubscribeMessageType.PAYLOAD:
        print("Event type: ", event.eventType)
        print("Event time: ", event.eventTime)
        print("Symbol: ", event.symbol)
        print("Data:")
        is_buyer_maker = getattr(event, 'isBuyerMaker')
        if is_buyer_maker:
            print('isBuyerMaker  ', is_buyer_maker)
            market_price = getattr(event, 'price')
            share_item.set('market_price_usdt', market_price)
        # PrintBasic.print_obj(event)
    else:
        print("Unknown Data:")
    print()


def error(e: 'BinanceApiException'):
    print(e.error_code + e.error_message)


if __name__ == '__main__':
    sub_client.subscribe_aggregate_trade_event("btcusdt", callback, error)
    share_communication_start()
    print('行情websocket服务启动成功')
