# -*- coding: utf-8 -*-

import time
import random

from flask_testing import TestCase

from apps import db, tc_sms, create_app
from apps.utils import Utils
from apps.models import User, AdminUser
from apps.auths import Auth
from config import config


class BaseCase(TestCase):
    verify_info = {}
    image_info = {}

    def hook_sender(self, phone, params, verify_type):
        self.verify_info = {"mobile": phone, "code": params[0], "minutes": params[1], "type": verify_type}
        return {"result": 0}

    def hook_upload_image(self, img_name, file_bytes):
        url = "http://%s.com" % random.choice("abcdef")
        self.image_info = {"name": img_name, "file_bytes": file_bytes, "url": url}
        return url

    @staticmethod
    def delete_tables(tables):
        for table in tables:
            db.session.query(table).delete()
        db.session.commit()

    def create_app(self):
        from celerys.tasks import celery

        celery.config_from_object(config["testing"])
        app = create_app("testing")
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()
        tc_sms.send_sms = self.hook_sender

    def prepare_user(self, nickname="15020202200"):

        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            user = User(nickname=nickname,password=Utils.set_password('123456'), discount_tag='NO', status='normal')
            db.session.add(user)
            db.session.commit()
        Auth().authenticate(user, self.app.config['USER_TOKEN_USEFUL_DATE'], self.app.config['SECRET_KEY'])
        return user

    def prepare_admin(self, nickname="admin100", password="123456"):
        admin = AdminUser.query.filter_by(nickname=nickname).first()
        if not admin:
            admin = AdminUser(nickname=nickname, password=Utils.set_password(password))
            db.session.add(admin)
            db.session.commit()
        Auth().authenticate_admin_user(admin, self.app.config['USER_TOKEN_USEFUL_DATE'], self.app.config['SECRET_KEY'])
        return admin

