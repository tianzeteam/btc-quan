from datetime import timedelta

# 指定broker
BROKER_URL = 'redis://127.0.0.1:6379'
# 指定backend
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# 指定时区
CELERY_TIMEZONE = 'Asia/Shanghai'

# 指定导入的任务模块
CELERY_IMPORTS = (
    'celerys.tasks',
)

# 定时调度schedules
CELERYBEAT_SCHEDULE = {
    'roll_discount_price_job': {
        'task': 'celerys.tasks.roll_discount_price_job',
        'schedule': timedelta(seconds=60),  # 每60秒执行一次
        'args': (),  # 任务函数参数
        'options': {'queue': 'CELERY_SCHEDULE_QUEUE'}
    },
    'roll_get_position_job': {
        'task': 'celerys.tasks.roll_get_position_job',
        'schedule': timedelta(seconds=10),  # 每10秒执行一次
        'args': (),  # 任务函数参数
        'options': {'queue': 'CELERY_SCHEDULE_QUEUE'}
    }
}
