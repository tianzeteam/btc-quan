# -*- coding: utf-8 -*-
import logging
from apps.utils import *
from decimal import Decimal
from sqlalchemy import *
from apps.models import db, User, Flowlog,CommonSetting, RunStatus,BonusScene,Position,CloseTimes
from apps import log_builder
from apps.utils import Utils
import config
logger = logging.getLogger(__name__)


class CoreHandleProcess:

    def __init__(self):
        pass

    # 做多处理流程
    def repeat_handle_target_long(self, binance_client, user, update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                  _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting):
        price_interval_time = setting.price_interval_time
        wait_interval_update_time = setting.wait_interval_update_time
        close_difference = setting.close_difference
        once_amt = setting.once_amount
        is_long = setting.is_long
        amount_of_market_price = setting.amount_of_market_price

        # step3 获取持仓均价和持仓量
        entry_price, position_amt = binance_client.get_position_info(symbol)

        # step4 获取当前市场价格
        next_update_price = binance_client.get_recent_trades(symbol)

        # step5 策略主流程
        # A开仓逻辑
        if position_amt < float(amount_of_market_price):
            open_price = Utils.get_open_price(symbol)
            sub_price = CoreHandleProcess.get_market_diff_price(binance_client, user, symbol, update_price, setting, bonus_setting)

            if _FIRST_HIT_OPEN_PRICE:
                # LONG 开仓刷新价格条件判定
                print("next_update_price:{}  update_price:{}".format(next_update_price, update_price))
                if float(next_update_price) <= float(update_price):
                    log_builder.log_update_open_success(user, price=str(next_update_price))
                    _FIRST_HIT_OPEN_PRICE = True
                    time.sleep(wait_interval_update_time)
                    self.repeat_handle_target_long(binance_client, user, next_update_price, symbol,
                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                   bonus_setting)

                else:
                    log_builder.log_update_open_fail(user=user, price=str(next_update_price))  # 刷新开仓最低价失败，当前价格：{}，准备买入...
                    order_id, status = binance_client.market_order(symbol, 'BUY', Decimal(once_amt).quantize(Decimal('0.0000')))
                    if order_id and status == 'NEW':
                        log_builder.log_open_success(user=user, price=next_update_price)
                    time.sleep(price_interval_time)
                    _FIRST_HIT_OPEN_PRICE = False
                    self.repeat_handle_target_long(binance_client, user, next_update_price, symbol,
                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                   bonus_setting)

            elif CoreHandleProcess.match_first_hit_price(is_long=is_long, open_price=open_price,
                                                         market_price=next_update_price, sub_price=sub_price) and next_update_price > 0:
                log_builder.log_update_hit_open_price(user, price=next_update_price)
                time.sleep(wait_interval_update_time)
                _FIRST_HIT_OPEN_PRICE = True
                self.repeat_handle_target_long(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                               _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
        # step5 策略主流程
        # B 平仓逻辑
        if position_amt > 0:
            if _FIRST_HIT_CLOSE_PRICE:
                # 获取当前市场价格
                # print("next_update_price:{}  update_price:{}".format(next_update_price, update_price))
                if float(next_update_price) >= float(update_price):
                    log_builder.log_update_close_success(user, price=str(next_update_price))

                    time.sleep(wait_interval_update_time)
                    _FIRST_HIT_CLOSE_PRICE = True
                    self.repeat_handle_target_long(binance_client, user, next_update_price, symbol,
                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                   bonus_setting)

                else:
                    log_builder.log_update_close_fail(user=user,
                                                      price=str(next_update_price))  # 刷新开仓最低价失败，当前价格：{}，准备买入...
                    order_id, status = binance_client.market_order(symbol, 'SELL',
                                                                   Decimal(abs(position_amt)).quantize(
                                                                       Decimal('0.0000')))
                    if order_id and status == 'NEW':
                        profit_amt = Decimal((next_update_price - entry_price) * position_amt).quantize(
                            Decimal('0.0000'))
                        log_builder.log_close(user, position_amt=position_amt, profit_amt=profit_amt,
                                              entry_price=entry_price, price=next_update_price)
                        run_status = db.session.query(RunStatus).filter(RunStatus.user_id == user.id).first()
                        close_times = db.session.query(CloseTimes).filter(and_(CloseTimes.user_id == user.id,
                                                                               CloseTimes.task_pipe_id == run_status.task_pipe_id)).first()
                        close_times.close_times = close_times.close_times+1
                        db.session.commit()

                    time.sleep(price_interval_time)
                    _FIRST_HIT_CLOSE_PRICE = False
                    self.repeat_handle_target_long(binance_client, user, next_update_price, symbol,
                                                   _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                   bonus_setting)

            elif (next_update_price - entry_price) >= close_difference and next_update_price > 0:
                log_builder.log_update_hit_open_price(user, price=next_update_price)

                time.sleep(wait_interval_update_time)
                _FIRST_HIT_CLOSE_PRICE = True
                self.repeat_handle_target_long(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                               _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
        # step6 重新执行主流程
        time.sleep(price_interval_time)
        self.repeat_handle_target_long(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                       _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)

    # 做空处理流程
    def repeat_handle_target_short(self, binance_client, user, update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                   _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting):
        price_interval_time = setting.price_interval_time
        wait_interval_update_time = setting.wait_interval_update_time
        once_amt = setting.once_amount
        is_long = setting.is_long
        amount_of_market_price = setting.amount_of_market_price
        close_diff_price = setting.close_difference
        entry_price, position_amt = binance_client.get_position_info(symbol)
        next_update_price = binance_client.get_recent_trades(symbol)
        print('abs(position_amt){}  amount_of_market_price:{}'.format(abs(position_amt),amount_of_market_price))
        if abs(position_amt) < float(amount_of_market_price):
            open_price = Utils.get_open_price(symbol)
            sub_price = CoreHandleProcess.get_market_diff_price(binance_client, user, symbol, update_price,
                                                                setting, bonus_setting)
            if _FIRST_HIT_OPEN_PRICE:
                # step4 获取当前市场价格
                print("next_update_price:{}  update_price:{}".format(next_update_price, update_price))
                if float(next_update_price) > float(update_price):
                    log_builder.log_update_open_success(user, price=str(next_update_price))

                    time.sleep(wait_interval_update_time)
                    _FIRST_HIT_OPEN_PRICE = True
                    self.repeat_handle_target_short(binance_client, user, next_update_price, symbol,
                                                    _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                    bonus_setting)

                else:
                    log_builder.log_update_open_fail(user=user, price=str(next_update_price))  # 刷新开仓最低价失败，当前价格：{}，准备买入...
                    order_id, status = binance_client.market_order(symbol, 'SELL',
                                                                   Decimal(once_amt).quantize(Decimal('0.0000')))
                    if order_id and status == 'NEW':
                        log_builder.log_open_success(user=user, price=next_update_price)

                    time.sleep(price_interval_time)
                    _FIRST_HIT_OPEN_PRICE = False
                    self.repeat_handle_target_short(binance_client, user, next_update_price, symbol,
                                                    _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                    bonus_setting)

            elif CoreHandleProcess.match_first_hit_price(is_long=is_long, open_price=open_price,
                                                         market_price=next_update_price, sub_price=sub_price) and next_update_price > 0:
                log_builder.log_update_hit_open_price(user, price=next_update_price)
                time.sleep(wait_interval_update_time)
                _FIRST_HIT_OPEN_PRICE = True
                self.repeat_handle_target_short(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                                _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
        # step5 策略主流程
        # B 平仓逻辑
        if position_amt < 0:

            if _FIRST_HIT_CLOSE_PRICE:
                #  SHORT 平仓刷新价格条件判定
                print("next_update_price:{}  update_price:{}".format(next_update_price, update_price))
                if float(next_update_price) < float(update_price):
                    log_builder.log_update_close_success(user, price=str(next_update_price))
                    time.sleep(wait_interval_update_time)
                    _FIRST_HIT_CLOSE_PRICE = True
                    self.repeat_handle_target_short(binance_client, user, next_update_price, symbol,
                                                    _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                    bonus_setting)

                else:
                    log_builder.log_update_close_fail(user=user,
                                                      price=str(next_update_price))  # 刷新平仓最低价失败，当前价格：{}，准备买入...
                    order_id, status = binance_client.market_order(symbol, 'BUY',
                                                                   Decimal(abs(position_amt)).quantize(Decimal('0.0000')))
                    if order_id and status == 'NEW':
                        profit_amt = Decimal((next_update_price - entry_price) * position_amt).quantize(
                            Decimal('0.0000'))
                        log_builder.log_close(user, position_amt=position_amt, profit_amt=profit_amt,
                                              entry_price=entry_price, price=next_update_price)
                    time.sleep(price_interval_time)
                    _FIRST_HIT_CLOSE_PRICE = False
                    self.repeat_handle_target_short(binance_client, user, next_update_price, symbol,
                                                    _FIRST_HIT_OPEN_PRICE, _FIRST_HIT_CLOSE_PRICE, setting,
                                                    bonus_setting)

            elif (entry_price - next_update_price) >= close_diff_price and next_update_price > 0:
                log_builder.log_update_hit_close_price(user, entry_price=entry_price, price=next_update_price)
                time.sleep(wait_interval_update_time)
                _FIRST_HIT_CLOSE_PRICE = True
                self.repeat_handle_target_short(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                                _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)
        # step6 重新执行主流程
        time.sleep(price_interval_time)
        self.repeat_handle_target_short(binance_client, user, next_update_price, symbol, _FIRST_HIT_OPEN_PRICE,
                                        _FIRST_HIT_CLOSE_PRICE, setting, bonus_setting)

    @staticmethod
    def match_first_hit_price(is_long, open_price, market_price, sub_price):
        if is_long == 'LONG':
            print('{} {} {}'.format(open_price, market_price, sub_price))
            return open_price - market_price >= sub_price
        else:
            return market_price - open_price >= sub_price

    @staticmethod
    def get_market_diff_price(binance_client_api, user, symbol, market_price, setting, bonus_setting):
        is_long = setting.is_long
        try:
            entry_price, position_amt = binance_client_api.get_position_info(symbol=symbol)
        except:
            log_builder.log_fail_position(user)
            return 10000
        amount_of_market_price = setting.amount_of_market_price
        difference_of_market_price = setting.difference_of_market_price
        dynamic_1_price = setting.dynamic_1_price
        dynamic_2_price = setting.dynamic_2_price
        difference_dynamic_1_price = setting.dynamic_1_price
        difference_dynamic_2_price = setting.dynamic_2_price
        hit1_position = abs(float(amount_of_market_price) * float(dynamic_1_price) / float(100))
        hit2_position = abs(float(amount_of_market_price) * float(dynamic_2_price) / float(100))
        now_time = int(time.time())
        bonus_start_time = Utils.time2second(bonus_setting.start_time)
        bonus_end_time = Utils.time2second(bonus_setting.end_time)
        bonus_amt = bonus_setting.bonus_amount

        sub_price = (float(entry_price) - float(market_price)) * (float(1) if is_long == 'LONG' else float(-1))
        position_amt = abs(position_amt)
        if position_amt > hit1_position:
            if hit1_position <= position_amt <= hit2_position and sub_price >= difference_dynamic_1_price:
                return -100 if is_long == 'LONG' else 100
            elif position_amt >= hit2_position and sub_price >= difference_dynamic_2_price:
                return -100 if is_long == 'LONG' else 100
            else:
                return 10000 if is_long == 'LONG' else -10000
        elif bonus_start_time < now_time < bonus_end_time:
            if position_amt < bonus_amt:
                return bonus_setting.bonus_diff
            else:
                return round(difference_of_market_price, 2)
        else:
            return round(difference_of_market_price, 2)




