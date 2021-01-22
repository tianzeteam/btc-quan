# -*- coding: utf-8 -*-

import time
import json
from decimal import Decimal
from traceback import print_exc
from flask import g,jsonify, current_app, request
import logging
from apps.market import mv
from .price import get_prices,get_discount_tag


# create logger
logger = logging.getLogger(__name__)

mv.add_url_rule('/market/prices', view_func=get_prices, methods=['GET'])

mv.add_url_rule('/market/discount', view_func=get_discount_tag, methods=['GET'])


