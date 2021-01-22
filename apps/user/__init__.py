from flask import Blueprint


uv = Blueprint("user",  __name__, url_prefix="/api")

from . import views

