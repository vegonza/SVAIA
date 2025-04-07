from flask import Flask
from .models import db
from .routes import sql_bp

__all__ = ["sql_bp"]


def init_sql(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()
