# coding: utf-8

import os
import sys
import logging

from flask_apscheduler import APScheduler
from flask_docs import ApiDoc
from flask_cors import CORS
from flask_request_params import bind_request_params
from flask_migrate import Migrate, MigrateCommand  # 导入
from flask_script import Manager  # 导入

from apps import create_app
from apps import db
from apps.get_middleware import StripContentTypeMiddleware
from SchedulerService import SchedulerApi
from apps.log_builder import LogBuilder
logger = logging.getLogger(__name__)
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
print(os.getenv('FLASK_CONFIG'))
app.before_request(bind_request_params)
ApiDoc(app)

manager = Manager(app)

# 第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
Migrate(app, db)  # 实例化对象时，会自动将Migrate对象注入到app中，让app和db对象产生关联。

# manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db', MigrateCommand)  # 'db'命令名可以任意

CORS(app, resources={r"/*": {"origins": "*"}})
app.wsgi_app = StripContentTypeMiddleware(app.wsgi_app)
ap_scheduler = APScheduler()
ap_scheduler.init_app(app)
scheduler_api = SchedulerApi(db)


def init_service():
    with app.app_context():
        scheduler_api.task_get_open_price_job()


def scheduler_discount_price():
    with app.app_context():
        SchedulerApi.task_discount_tag_job(bind_db=db, app=app, user=None)


def scheduler_get_position():
    with app.app_context():
        scheduler_api.task_get_position_job(bind_db=db, app=app, user=None)


def scheduler_task_check_complete():
    with app.app_context():
        scheduler_api.task_check_complete_job(bind_db=db, app=app, user=None)


def scheduler_process_pipe():
    with app.app_context():
        scheduler_api.task_process_pipe_job(app=app)


def scheduler_get_open_price():
    with app.app_context():
        scheduler_api.task_get_open_price_job()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.info('系统准备启动了::: ')
    ap_scheduler.add_job(func=scheduler_discount_price, id='scheduler_discount_price', max_instances=10,
                         trigger='interval', seconds=600000)
    ap_scheduler.add_job(func=scheduler_get_position, id='scheduler_get_position', max_instances=10, trigger='interval', seconds=10000)
    ap_scheduler.add_job(func=scheduler_task_check_complete, id='scheduler_task_check_complete', max_instances=20,
                         trigger='interval', seconds=1000)
    ap_scheduler.add_job(func=scheduler_process_pipe, id='scheduler_process_pipe', trigger='cron', day_of_week='0-6',
                         hour=0, minute=0, second=0, replace_existing=True)
    ap_scheduler.add_job(func=scheduler_get_open_price, id='scheduler_get_open_price', max_instances=1,
                          trigger='interval',
                          seconds=6000)

    ap_scheduler.start()
    init_service()  # 服务器初始化资源
    app.run(port=3389)

