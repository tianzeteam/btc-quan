from flask import Blueprint


mv = Blueprint("market",  __name__, url_prefix="/api")

from . import views
