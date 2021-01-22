from apps import create_app
from apps import db
import os
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    db.drop_all()
    db.create_all()