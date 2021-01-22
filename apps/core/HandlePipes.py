import sys
from apps.utils import Utils
from apps.common import async_func
from sqlalchemy import *
import time
from decimal import Decimal
from binance_d.exception.binanceapiexception import BinanceApiException as D_BinanceApiException
from binance_f.exception.binanceapiexception import BinanceApiException as F_BinanceApiException
from apps.models import RunStatus, CommonSetting, CloseTimes, BonusScene,db,User
from apps.binance_user_api import BinanceUserApi
from apps import log_builder
from apps.core.CoreHandleProcess import CoreHandleProcess
from traceback import print_exc
handle_process_maker = CoreHandleProcess()


class HandlePipes(object):
    def __init__(self):
        pass

    @async_func
    def run(self,  app, user_id):
        with app.app_context():
            run_status = db.session.query(RunStatus).filter(and_(RunStatus.user_id == user_id,
                                                                 RunStatus.status == 'ready')).first()

            if not run_status:
                return
            run_status.status = 'active'
            db.session.commit()
            task_pipe_id = run_status.task_pipe_id
            if not task_pipe_id:
                task_pipe_id = Utils.get_system_no(Utils)
                run_status.task_pipe_id = task_pipe_id
                close_times = CloseTimes(user_id=user_id, task_pipe_id=task_pipe_id, close_times=0)
                db.session.add(close_times)
                db.session.commit()

            setting = db.session.query(CommonSetting).filter(CommonSetting.user_id == user_id).first()
            bonus_setting = db.session.query(BonusScene).filter(BonusScene.user_id == user_id).first()

            # 常规设置数据读取
            is_usdt = setting.is_usdt
            is_long = setting.is_long
            is_limit_price = setting.is_limit_price
            price_interval_time = setting.price_interval_time
            user = db.session.query(User).filter(User.id == user_id).first()
            symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
            scheduler_binance_client = BinanceUserApi(app, user)

            try:
                # step1 获取0点合约价格
                open_price = Utils.get_open_price(symbol)
                if not open_price:  # 0点开盘价格有效性检查
                    return

                # step2 先取消所有限价单
                if is_limit_price == 'YES':
                    scheduler_binance_client.cancel_all_orders(symbol)
                    list_difference_of_limit_price = setting.list_difference_of_limit_price
                    list_difference_of_limit_amount = setting.list_difference_of_limit_amount
                    limit_append_list = zip(list_difference_of_limit_price, list_difference_of_limit_amount)
                    recent_price = scheduler_binance_client.get_recent_trades(symbol)
                    if float(recent_price) > float(30000) or float(recent_price) < float(10000):  # 最近成交价格有效性检查
                        time.sleep(price_interval_time)
                        recent_price = scheduler_binance_client.get_recent_trades(symbol)

                    for diff_price, quantity in limit_append_list:
                        if is_long == 'LONG':
                            price = float(recent_price) - float(diff_price)
                            scheduler_binance_client.limit_order(symbol=symbol, side='BUY', quantity=float(quantity),
                                                                 price=Decimal(price).quantize(Decimal('0.00')))
                        else:
                            price = float(recent_price) + float(diff_price)
                            scheduler_binance_client.limit_order(symbol=symbol, side='SELL', quantity=float(quantity),
                                                                 price=Decimal(price).quantize(Decimal('0.00')))
                    log_builder.log_limit_order_success(user)

                _FIRST_HIT_OPEN_PRICE = False   # 默认第一次符合开仓条件 为false
                _FIRST_HIT_CLOSE_PRICE = False  # 默认第一次符合平仓条件 为false
                update_price = scheduler_binance_client.get_recent_trades(symbol)
                if update_price == float(0.0):
                    time.sleep(price_interval_time)
                    update_price = scheduler_binance_client.get_recent_trades(symbol)

                # step4 执行处理函数
                if is_long == 'LONG':
                    handle_process_maker.repeat_handle_target_long(scheduler_binance_client, user, update_price, symbol,
                                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE,
                                                                   setting, bonus_setting)
                else:
                    handle_process_maker.repeat_handle_target_short(scheduler_binance_client, user, update_price,
                                                                    symbol, _FIRST_HIT_OPEN_PRICE,
                                                                    _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
            except D_BinanceApiException:
                print('D_BinanceApiException ')
                if is_long == 'LONG':
                    handle_process_maker.repeat_handle_target_long(scheduler_binance_client, user, update_price, symbol,
                                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE,
                                                                   setting, bonus_setting)
                else:
                    handle_process_maker.repeat_handle_target_short(scheduler_binance_client, user, update_price,
                                                                    symbol, _FIRST_HIT_OPEN_PRICE,
                                                                    _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)

            except F_BinanceApiException:
                print('F_BinanceApiException ')
                if is_long == 'LONG':
                    handle_process_maker.repeat_handle_target_long(scheduler_binance_client, user, update_price, symbol,
                                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE,
                                                                   setting, bonus_setting)
                else:
                    handle_process_maker.repeat_handle_target_short(scheduler_binance_client, user, update_price,
                                                                    symbol, _FIRST_HIT_OPEN_PRICE,
                                                                    _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
            except:
                print_exc(limit=10)


