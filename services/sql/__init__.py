from flask import Flask
from .models import db, User
from .routes import sql_bp

__all__ = ["sql_bp"]


def init_sql(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin', email='admin@admin.com')
            default_user = User(username='user', password='user', email='user@user.com')
            db.session.add_all([admin, default_user])
            db.session.commit()
