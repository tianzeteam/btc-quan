# -*- coding: utf-8 -*-

import re
import time

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import class_mapper, synonym
from sqlalchemy import Column, Enum, JSON, String
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, VARCHAR, DECIMAL,FLOAT,DATE

from . import db

IMAGE_PATTERN = re.compile(r".*\.(png|jpg|jpeg|bmp|gif)", re.I)


def current_timestamp(*args, **kwargs):
    return int(time.time())


class BaseModel(db.Model):
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseModel):
    """用户"""
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(60), unique=False, index=False)
    password = db.Column(db.String(255), unique=False, index=False, comment='密码')
    telephone = db.Column(db.String(12), nullable=True, comment='手机')
    access_token = db.Column(db.String(255), unique=False, index=False)
    api_key = db.Column(db.String(160), unique=False, index=False)
    api_secret = db.Column(db.String(160), unique=False, index=False)
    login_time = db.Column(db.INTEGER(), default=current_timestamp)
    create_time = db.Column(db.INTEGER(), default=current_timestamp)
    discount_tag = db.Column(db.Enum('YES', 'NO',  name='discount_tag'))
    status = db.Column(db.Enum('normal', 'pending', 'del', name='status'))

    def get_user_info(self):
        """
                获取当前用户基本信息
                :return:
                """
        return self.nickname, self.telephone


class AdminUser(BaseModel):
    """用户"""
    __tablename__ = 'Admin_User'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(60), unique=False, index=False)
    password = db.Column(db.String(255), unique=False, index=False, comment='密码')
    access_token = db.Column(db.String(1500), unique=False, index=False)
    login_time = db.Column(db.INTEGER(), default=current_timestamp)
    create_time = db.Column(db.INTEGER(), default=current_timestamp)
    status = db.Column(db.Enum('normal', 'del', name='status'), unique=False, index=True)


class Flowlog(BaseModel):
    __tablename__ = 'Flowlog'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())
    content = db.Column(db.String(255))
    log_type = db.Column(db.Enum('OPEN_SUCCESS',  'CLOSE', 'START', 'FINISH', 'UPDATE_CLOSE_FAIL',
                                 'UPDATE_OPEN_PRICE_FAIL',
                                 'LIMIT_ORDER_SUCCESS', 'FAIL_QUERY_POSITION','UPDATE_OPEN_PRICE_SUCCESS',
                                 'UPDATE_HIT_OPEN_PRICE', name='log_type'))
    create_time = db.Column(db.INTEGER(), default=current_timestamp)


class RunStatus(BaseModel):
    __tablename__ = 'Run_Status'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())

    today = db.Column(db.DATE())
    close_times = db.Column(db.INTEGER(), default=0)
    status = db.Column(db.Enum('active', 'ready', 'stop', name='status'), default='stop')
    task_status = db.Column(db.Enum('finish', 'run', name='task_status'), default='run')
    task_pipe_id = db.Column(db.String(64))
    update_time = db.Column(db.INTEGER(), default=current_timestamp)


class CloseTimes(BaseModel):
    __tablename__ = 'Close_Times'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())
    task_pipe_id = db.Column(db.String(64))
    today = db.Column(db.DATE())
    close_times = db.Column(db.INTEGER(), default=0)


class Fangtang(BaseModel):
    """方糖设置"""
    __tablename__ = 'Fangtang'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())
    title = db.Column(db.String(80, 'utf8mb4_bin'), comment='消息标题')
    api_key = db.Column(db.String(120), unique=False, index=False)
    api_secret = db.Column(db.String(120), unique=False, index=False)
    ft_key = db.Column(db.String(120), unique=False, index=False)
    create_time = db.Column(db.INTEGER(), default=current_timestamp, comment='创建时间')
    update_time = db.Column(db.INTEGER(), default=current_timestamp, comment='更新时间', onupdate=current_timestamp)


class BonusScene(BaseModel):
    """彩蛋设置"""
    __tablename__ = 'Bonus_Setting'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())
    start_time = db.Column(db.INTEGER(), default=0, comment='起始时间')
    end_time = db.Column(db.INTEGER(), default=0, comment='截止时间')
    bonus_diff = db.Column(db.INTEGER(), comment='彩蛋差价')
    bonus_amount = db.Column(db.FLOAT(), comment='彩蛋数量')
    create_time = db.Column(db.INTEGER(), default=current_timestamp, comment='创建时间')
    update_time = db.Column(db.INTEGER(), default=current_timestamp, comment='更新时间')


class CommonSetting(BaseModel):
    """常规设置"""
    __tablename__ = 'Common_Setting'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)     # 参与用户ID
    once_amount = db.Column(db.Float, unique=False, index=False)  # 单次数量
    close_difference = db.Column(db.Integer, unique=False, index=False)  # 平仓差价
    amount_of_market_price = db.Column(db.Float, unique=False, index=False)  # 市价总量
    difference_of_market_price = db.Column(db.Integer, unique=False, index=False)  # 市价差价
    list_difference_of_limit_price = db.Column(db.JSON, unique=False, index=False)  # 限价差价数组
    list_difference_of_limit_amount = db.Column(db.JSON, unique=False, index=False)  # 限价数量数组
    dynamic_1_price = db.Column(db.Integer, unique=False, index=False)  # 动态价格1点百分比
    difference_dynamic_1_price = db.Column(db.Integer, unique=False, index=False)  # 动态价格1点价差
    dynamic_2_price = db.Column(db.Integer, unique=False, index=False)  # 动态价格2点百分比
    difference_dynamic_2_price = db.Column(db.Integer, unique=False, index=False)  # 动态价格点2价差
    is_limit_price = db.Column(db.Enum('YES', 'NO', name='is_limit_price'), default='NO')  # 是否添加限价单
    is_usdt = db.Column(db.Enum('USDT', 'COIN', name='is_usdt'), default='USDT')  # 是否是U本位,COIN 本位
    is_long = db.Column(db.Enum('LONG', 'SHORT', name='is_long'), default='LONG')  # 是否做多

    price_interval_time = db.Column(db.Integer, unique=False, index=False)  # 当前价格查询间隔时间
    wait_interval_update_time = db.Column(db.Integer, unique=False, index=False)  # 刷新价格等待间隔时间

    auto_start_time = db.Column(db.Integer, unique=False, index=False)  # 自动平仓起始时间
    auto_close_price_per = db.Column(db.Integer, unique=False, index=False)  # 自动平仓价格百分比

    create_time = db.Column(db.Integer, unique=False, index=True)


class Position(BaseModel):
    """仓位数据"""
    __tablename__ = 'Position'

    id = db.Column(db.BIGINT(), primary_key=True)
    user_id = db.Column(db.BIGINT())
    symbol = db.Column(db.String(30), unique=False, index=False)
    entry_price = db.Column(db.FLOAT(), comment='仓位均价')
    position_amount = db.Column(db.FLOAT(), comment='仓位数量')
    create_time = db.Column(db.INTEGER(), default=current_timestamp, comment='创建时间')
    update_time = db.Column(db.INTEGER(), default=current_timestamp, comment='更新时间')


