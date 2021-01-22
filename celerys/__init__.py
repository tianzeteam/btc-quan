# -*- coding: utf-8 -*-

from celery import Celery


def create_celery():
    # 创建celery实例
    btcbot_api = Celery('btcbot_api')
    # 通过celery实例加载配置模块
    btcbot_api.config_from_object('celerys.celeryconfig')
    return btcbot_api
