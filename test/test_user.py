# coding:utf-8
"""
description: 用户测试
author: jiangyx3915
date: 2019-05-25
"""


from apps.models import User, db, CommonSetting, CloseTimes
from test.base import BaseCase
from process_communication import *
from apps.utils import *
import config


class TestUser(BaseCase):


    @staticmethod
    def generate_users():
        user1 = User(nickname='user1', status='normal')

        db.session.add(user1)
        db.session.commit()

    def setUp(self):
        super().setUp()
        # self.generate_users()
        self.telephone = "19919964645"
        user = self.prepare_user(nickname=self.telephone)
        self.user_id = user.id
        self.user_headers = {"Authorization": "JWT " + user.access_token}
        admin_user = self.prepare_admin(nickname='admin100')
        self.admin_user_id = admin_user.id
        self.admin_user_headers = {"Authorization": "JWT " + admin_user.access_token}

    def tearDown(self):
        # self.delete_tables([User])
        pass

    def test_limit_price_list(self):
        setting = CommonSetting.query.filter(CommonSetting.user_id == 12).first()
        list_difference_of_limit_price = setting.list_difference_of_limit_price
        list_difference_of_limit_amount = setting.list_difference_of_limit_amount
        print(type(list_difference_of_limit_price))
        print(list_difference_of_limit_price)

    def test_block_user(self):
        """
        测试封禁用户
        :return:
        """
        user = User.query.filter_by(telephone='18926157202').first()
        assert user.status == 'normal'
        response = self.client.delete(f'/platform/user/{user.id}', headers=self.admin_user_headers)
        data = response.json
        assert data["code"] == "success"
        user = User.query.filter_by(telephone='18926157202').first()
        assert user.status == 'del'

    def test_change_user_password(self):
        """
        测试修改用户密码
        :return:
        """
        user = User.query.filter_by(nickname='18926157202').first()
        assert user.status == 'normal'
        response = self.client.put(f'/platform/user/password', json={"user_id": user.id, "password": "12345678"},
                                   headers=self.admin_user_headers)
        data = response.json
        assert data["code"] == "success"
        post_json = {
            "nickname": "18926157202",
            "password": "12345678"

        }
        response = self.client.post("/api/login", json=post_json)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_search_user_logs(self):
        """
        测试查询用户log
        :return:
        """
        # 查询名称
        rule = {
            "nickname": 'user1'
        }
        response = self.client.get('/api/user/logs?sort=desc', headers=self.user_headers)
        assert response.status_code == 200

    def test_update_phone(self):
        phone = "13933334444"
        response = self.client.put("/api/user/phone/", json={"phone": phone}, headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"

    def test_user_login(self):
        post_json = {
            "nickname": "19919964645",
            "password": "123456"

        }
        response = self.client.post("/api/login", json=post_json)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_get_common_setting(self):
        response = self.client.get("/api/common/setting", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_get_discount_tag(self):
        response = self.client.get("/api/market/discount", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_change_bonus_setting(self):
        post_json = {
            "start_time": 3,
            "end_time": 8,
            "bonus_diff": 70,
            "bonus_amount": 0.03

        }
        response = self.client.put("/api/bonus/setting", json=post_json, headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_get_bonus_setting(self):
        response = self.client.get("/api/bonus/setting", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_user_position(self):
        response = self.client.get("/api/user/position", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_market_prices(self):
        response = self.client.get("/api/market/prices", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_get_orders(self):
        response = self.client.get("/api/user/orders", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_get_open_price(self):
        response = self.client.get("/api/market/prices", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_close_user_position(self):
        response = self.client.delete("/api/user/position", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_cancel_user_orders(self):
        response = self.client.delete("/api/user/orders", headers=self.user_headers)
        data = response.json
        print(data)
        assert data["code"] == "success"

    def test_get_runstatus(self):
        response = self.client.get("/api/user/runstatus", headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_change_runstatus(self):
        response = self.client.put("/api/user/runstatus", json={"curr_status": "ready"}, headers=self.user_headers)
        data = response.json
        assert data["code"] == "success"
        print(data)

    def test_manager_client(self):
        # 进程间共享变量
        manager_client = ManagerClient(config.MANAGER_DOMAIN, config.MANAGER_PORT, config.MANAGER_AUTH_KEY)
        share_dict = manager_client.get_share_data()
        print(share_dict.get('market_price_usdt'))

    def test_add_CloseTimes(self):
        close_times = CloseTimes(user_id=18)
        db.session.add(close_times)
        db.session.commit()

        assert close_times.close_times == 0
