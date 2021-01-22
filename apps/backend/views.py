# -*- coding: utf-8 -*-

from apps.backend import bv

from apps.backend.login import login

from apps.backend.user import (
    block_user,
    search_user,
    add_user,
    change_password
)

bv.add_url_rule("/login", view_func=login, methods=["POST"])
bv.add_url_rule("/users", view_func=search_user, methods=["GET"])
bv.add_url_rule("/user/<int:user_id>", view_func=block_user, methods=["DELETE"])
bv.add_url_rule("/user", view_func=add_user, methods=["POST"])
bv.add_url_rule("/user/password", view_func=change_password, methods=["PUT"])
