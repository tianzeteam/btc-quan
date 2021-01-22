# -*- coding: utf-8 -*-

import logging


from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from traceback import print_exc

logger = logging.getLogger()


class TencentSms(object):

    def __init__(self):
        self.appid = ""
        self.key = ""
        self.app = None
        self.ssender = None

    def init_from_app(self, app):
        self.appid = app.config['SMS_APP_ID']
        self.key = app.config['SMS_APP_KEY']
        self.app = app
        self.ssender = SmsSingleSender(self.appid, self.key)

    def send_single(self, phone_number, content):
        try:
            result = self.ssender.send(0, 86, phone_number, content, extend="", ext="")
            print(result)
        except HTTPError as e:
            print(e)
        except Exception as e:
            print(e)

    def _send_templateid(self, phone_number, params, template_id):
        result = {}
        try:
            result = self.ssender.send_with_param(86, phone_number,template_id,
                                                  params,  extend="", ext="")  # 签名参数未提供或者为空时，会使用默认签名发送短信
        except HTTPError as e:
            print_exc(limit=5)
        except Exception as e:
            print_exc(limit=5)
        return result

    def send_sms(self, phone, params, verify_type):
        if verify_type == 'mch_register':
            result = self.send_mch_register(phone, params)
        elif verify_type == 'add_phone':
            result = self.send_add_phone(phone, params)
        elif verify_type == 'reset_pass':
            result = self.send_reset(phone, params)
        else:
            result = self.send_withdraw(phone, params)
        return result

    def send_add_phone(self, phone_number, params):
        result = self._send_templateid(phone_number, params, self.app.config['TELEPHONE_TEMPLATE_ID'])
        return result

    def send_reset(self, phone_number, params):
        result = self._send_templateid(phone_number, params, self.app.config['RESET_TEMPLATE_ID'])
        return result

    def send_mch_register(self, phone_number, params):
        result = self._send_templateid(phone_number, params, self.app.config['MERCHANT_TEMPLATE_ID'])
        return result

    def send_withdraw(self, phone_number, params):
        result = self._send_templateid(phone_number, params, self.app.config['WITHDRAW_TEMPLATE_ID'])
        return result
