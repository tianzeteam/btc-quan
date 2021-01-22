# -*- coding: utf-8 -*-

from flask import g, jsonify

from apps import db
from apps.utils import Utils
from apps.auths import Auth
from apps.models import User, AdminUser
from apps.common import identify_required, admin_identify_required
from test.base import BaseCase


class TestCommon(BaseCase):

    def tearDown(self):
        self.delete_tables([User, AdminUser])

    def test_identify_required(self):
        info = {"user": None}

        @self.app.route("/test")
        @identify_required
        def test():
            info["user"] = g.user
            return jsonify({"code": "success"})

        response = self.client.get("/test")
        assert response.status_code == 200
        assert response.get_json()["code"] == "error"

        user = User(telephone="15020202200", password=Utils.set_password("123456"))
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(nickname="15020202200").first()
        ret = Auth().authenticate(user, self.app.config['USER_TOKEN_USEFUL_DATE'], self.app.config['SECRET_KEY'])
        assert ret.get_json()["code"] == "success"
        response = self.client.get("/test", headers={"Authorization": "JWT " + user.access_token})
        assert response.status_code == 200
        assert response.get_json()["code"] == "success"
        assert info["user"].telephone == "15020202200"

    def test_admin_identify_required(self):
        info = {"admin": None}

        @self.app.route("/test")
        @admin_identify_required
        def test():
            info["admin"] = g.admin
            return jsonify({"code": "success"})

        response = self.client.get("/test")
        assert response.status_code == 200
        assert response.get_json()["code"] == "error"

        admin = AdminUser(nickname="15020202200", password=Utils.set_password("123456"))
        db.session.add(admin)
        db.session.commit()
        amdin = AdminUser.query.filter_by(nickname="15020202200").first()
        ret = Auth().authenticate_admin_user(amdin, self.app.config['USER_TOKEN_USEFUL_DATE'],
                                             self.app.config['SECRET_KEY'])
        print('admin token: ', admin.access_token)
        assert ret.get_json()["code"] == "success"
        response = self.client.get("/test", headers={"Authorization": "JWT " + amdin.access_token})
        assert response.status_code == 200
        assert response.get_json()["code"] == "success"

