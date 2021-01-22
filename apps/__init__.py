# -*- coding: utf-8 -*-

import flask
from flask_sqlalchemy import SQLAlchemy
from apps.log_builder import LogBuilder
from config import config
from .tencent_sms import TencentSms
from .redis_client import RedisClient
from .binance_client import BinanceClient

db = SQLAlchemy()
tc_sms = TencentSms()
redis_client = RedisClient()

binance_client = BinanceClient()
log_builder = LogBuilder()




def create_app(config_name):

    from apps.user import uv
    from apps.market import mv
    from apps.trade import tv
    from apps.backend import bv
    app = flask.Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    log_builder.init_db(db)

    app.register_blueprint(uv)
    app.register_blueprint(mv)
    app.register_blueprint(tv)
    app.register_blueprint(bv)

    tc_sms.init_from_app(app)
    redis_client.init_from_app(app)
    binance_client.init_binance_from_app(app)


    return app
