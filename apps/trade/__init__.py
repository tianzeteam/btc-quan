from flask import Blueprint


tv = Blueprint("trade",  __name__, url_prefix="/api")

from . import views
