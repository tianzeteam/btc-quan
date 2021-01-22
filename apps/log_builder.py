
import sys
import datetime


class LogType:

    FINISH = '{} 恭喜今天任务已完成'
    CLOSE = '{} 恭喜！平仓成功，持仓{}张，持仓均价为{}，当前价格为{},盈利{} 元'
    OPEN_SUCCESS = '{}- 开仓成功，当前价格为{}'
    UPDATE_CLOSE_FAIL = '{} 刷新平仓失败，当前价格：{}，准备平仓...'
    UPDATE_OPEN_PRICE_FAIL = '{} 刷新开仓最低价失败，当前价格：{}，准备买入...'
    UPDATE_OPEN_PRICE_SUCCESS = '{} 刷新开仓价格成功，当前价格：{}，尝试继续刷新'
    UPDATE_HIT_OPEN_PRICE = '{} 第一次命中开仓价格，当前价格：{}，尝试继续刷新'
    UPDATE_CLOSE_PRICE_SUCCESS = '{} 刷新平仓价格成功，当前价格：{}，尝试继续刷新'
    UPDATE_HIT_CLOSE_PRICE = '{} 第一次命中平仓价格，持仓均价{}，当前价格：{}，尝试刷新新高价'
    LIMIT_ORDER_SUCCESS = '{} Binance 委托添加成功'
    START = '{}  开始运行…'
    FAIL_QUERY_POSITION = '{} 查询持仓信息失败'


class LogBuilder(object):
    def __init__(self):
        self.db = None  # 数据库实例子

    def init_db(self, db):
        self.db = db

    def log_fail_position(self, user):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.FAIL_QUERY_POSITION.format(log_time)
        flow_log = Flowlog(user_id=user.id, log_type='FAIL_QUERY_POSITION', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_finish(self, user):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.FINISH.format(log_time)
        flow_log = Flowlog(user_id=user.id, log_type='FINISH', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_close(self, user, **kwargs):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.CLOSE.format(log_time, kwargs['position_amt'],  kwargs['entry_price'], kwargs['price'], kwargs['profit_amt'])
        flow_log = Flowlog(user_id=user.id, log_type='CLOSE', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_open_success(self, user, **kwargs):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.OPEN_SUCCESS.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='OPEN_SUCCESS', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_close_fail(self, user, **kwargs):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_CLOSE_FAIL.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_CLOSE_FAIL', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_open_fail(self, user, **kwargs):

        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_OPEN_PRICE_FAIL.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_OPEN_PRICE_FAIL', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_open_success(self, user, **kwargs):

        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_OPEN_PRICE_SUCCESS.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_OPEN_PRICE_SUCCESS', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_close_success(self, user, **kwargs):

        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_CLOSE_PRICE_SUCCESS.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_CLOSE_PRICE_SUCCESS', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_hit_open_price(self, user, **kwargs):

        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_HIT_OPEN_PRICE.format(log_time, kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_HIT_OPEN_PRICE', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_update_hit_close_price(self, user, **kwargs):

        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.UPDATE_HIT_CLOSE_PRICE.format(log_time, kwargs['entry_price'], kwargs['price'])
        flow_log = Flowlog(user_id=user.id, log_type='UPDATE_HIT_CLOSE_PRICE', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()


    def log_limit_order_success(self, user):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.LIMIT_ORDER_SUCCESS.format(log_time)
        flow_log = Flowlog(user_id=user.id, log_type='LIMIT_ORDER_SUCCESS', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()

    def log_start(self, user):
        from apps.models import Flowlog
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = LogType.START.format(log_time)
        flow_log = Flowlog(user_id=user.id, log_type='START', content=content)
        self.db.session.add(flow_log)
        self.db.session.commit()



