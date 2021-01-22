from flask import Blueprint

bv = Blueprint("backend", __name__, url_prefix="/platform")

from . import views