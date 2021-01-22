#!/usr/bin/env python
# coding: utf-8

###############################################################
#   计划执行服务类
###############################################################

import sys
import datetime


import config
from apps.utils import Utils
from apps.common import *
from sqlalchemy import *

from apps import binance_client
from apps.core.HandlePipes import HandlePipes
from apps.models import *
from apps.binance_user_api import BinanceUserApi
from apps import log_builder
from apps.core.CoreHandleProcess import CoreHandleProcess

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

logger = logging.getLogger(__name__)

diff_price_maker = CoreHandleProcess()
quan_pipe = HandlePipes()


class SchedulerApi(object):
    def __init__(self, db):
        self.db = db    # 数据库实例子

    @staticmethod
    def task_get_open_price_job():
        today = str(datetime.date.today())
        usdt_key = today+'_BTCUSDT'
        if not (usdt_key in config.OPEN_PRICE_DATA):
            print('first usdt')
            usdt_open_price = binance_client.get_open_price("BTCUSDT")
            if usdt_open_price > 0:
                config.OPEN_PRICE_DATA[today+'_BTCUSDT'] = usdt_open_price

        coin_key = today + '_BTCUSD_PERP'
        if not (coin_key in config.OPEN_PRICE_DATA):
            print('first coin')
            coin_open_price = binance_client.get_open_price("BTCUSD_PERP")
            if coin_open_price > 0:
                config.OPEN_PRICE_DATA[today+'_BTCUSD_PERP'] = coin_open_price
        print(config.OPEN_PRICE_DATA)

    @staticmethod
    @iterate_user_func
    def task_discount_tag_job(bind_db, app, user):
        common_setting = bind_db.session.query(CommonSetting).filter(CommonSetting.user_id == user.id).first()
        is_usdt = common_setting.is_usdt
        curr_hour = datetime.datetime.now().hour
        auto_start_time = common_setting.auto_start_time

        scheduler_binance_client = BinanceUserApi(app, user)
        try:
            discount_tag = 'NO'
            if int(curr_hour) > int(auto_start_time):
                symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
                high_price = scheduler_binance_client.get_high_price(symbol, auto_start_time)
                open_price = Utils.get_open_price(symbol)

                if float(high_price) - float(open_price) < 80:
                    discount_tag = 'YES'
            user.discount_tag = discount_tag
            bind_db.session.commit()
        except:
            print_exc(limit=10)

    @staticmethod
    @iterate_user_func
    def task_get_position_job(bind_db, app, user):
        common_setting = bind_db.session.query(CommonSetting).filter(CommonSetting.user_id == user.id).first()
        is_usdt = common_setting.is_usdt

        scheduler_binance_client = BinanceUserApi(app, user)
        try:

            symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
            entry_price, position_amount = scheduler_binance_client.get_position_info(symbol=symbol)
            single_position = Position.query.filter(and_(Position.user_id == user.id, Position.symbol == symbol)).first()
            if single_position:
                single_position.entry_price = entry_price
                single_position.position_amount = position_amount

            else:
                single_position = Position(user_id=user.id, symbol=symbol,
                                           entry_price=entry_price, position_amount=position_amount)
                bind_db.session.add(single_position)
            bind_db.session.commit()
        except:
            print_exc(limit=10)

    @staticmethod
    @iterate_user_func
    def task_check_complete_job(bind_db, app, user):
        run_status = bind_db.session.query(RunStatus).filter(and_(RunStatus.user_id == user.id,
                                                                  RunStatus.status == 'active')).first()
        if not run_status:
            return
        task_pipe_id = run_status.task_pipe_id
        if not task_pipe_id:
            return
        setting = bind_db.session.query(CommonSetting).filter(CommonSetting.user_id == user.id).first()
        is_usdt = setting.is_usdt
        auto_start_time = setting.auto_start_time
        symbol = 'BTCUSDT' if is_usdt == 'USDT' else 'BTCUSD_PERP'
        position = bind_db.session.query(Position).filter(and_(Position.user_id == user.id,
                                                               Position.symbol == symbol)).first()
        if not position:
            return
        position_amt = position.position_amount
        close_info = bind_db.session.query(CloseTimes).filter(and_(CloseTimes.user_id == user.id,
                                                                   CloseTimes.task_pipe_id == task_pipe_id)).first()
        if not close_info:
            return
        close_times = close_info.close_times
        curr_hour = datetime.datetime.now().hour
        scheduler_binance_client = BinanceUserApi(app, user)
        try:
            if curr_hour >= auto_start_time and float(position_amt) == 0 and close_times > 0:
                scheduler_binance_client.cancel_all_orders(symbol=symbol)
                time.sleep(2)
                scheduler_binance_client.cancel_all_orders(symbol=symbol)

                bind_db.session.query(RunStatus).filter(and_(RunStatus.user_id == user.id,
                                                        RunStatus.status == 'active'))\
                    .update({"task_pipe_id": None, "status": "stop"})
                bind_db.session.commit()
                log_builder.log_finish(user)  # 记录日志


        except:
            print_exc(limit=10)

    def task_process_pipe_job(self, app):
        page = 1
        limit = 20
        while True:
            offset = (page - 1) * limit
            user_list = User.query.filter(User.status == 'normal').limit(limit).offset(offset)
            try:
                if user_list.first():
                    for user in user_list:
                        try:
                            quan_pipe.run(app=app, user_id=user.id)
                        except:
                            print_exc(limit=10)
                    page += 1
                else:
                    break
            except:
                print_exc(limit=10)



