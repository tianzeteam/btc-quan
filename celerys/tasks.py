# -*- coding: utf-8 -*-

import os
import sys
import time
import random
from traceback import print_exc
from sqlalchemy import and_
from celerys import create_celery
from celery import platforms

from apps import create_app

from apps.models import  User
from apps import db
from apps.utils import Utils
from SchedulerService import SchedulerApi

from apps import redis_client


platforms.C_FORCE_ROOT = True
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()

celery = create_celery()
scheduler_api = SchedulerApi(db)


@celery.task
def roll_discount_price_job():
    with app.app_context():
        scheduler_api.roll_discount_price_job(app)


