from flask import Blueprint, Flask

from .models import User, db
from .projects import projects_bp
from .users import users_bp
from ..auth.password_utils import hash

__all__ = ["projects_bp", "users_bp"]

sql_bp = Blueprint("sql", __name__)

sql_bp.register_blueprint(projects_bp, url_prefix="/projects")
sql_bp.register_blueprint(users_bp, url_prefix="/users")


def init_sql(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(name='admin').first():
            admin = User(
                name='admin', last_name='admin',
                password=hash('admin'), email='admin@admin.com', is_admin=True
            )

            default_user = User(
                name='user', last_name='user',
                password=hash('user'), email='user@user.com', is_admin=False
            )

            user1 = User(
                name='1', last_name='1',
                password=hash('1'), email='1@1.com', is_admin=False
            )

            user2 = User(
                name='2', last_name='2',
                password=hash('2'), email='2@2.com', is_admin=False
            )

            user3 = User(
                name='3', last_name='3',
                password=hash('3'), email='3@3.com', is_admin=False
            )

            user4 = User(
                name='4', last_name='4',
                password=hash('4'), email='4@4.com', is_admin=False
            )

            user5 = User(
                name='5', last_name='5',
                password=hash('6'), email='6@6.com', is_admin=False
            )

            user6 = User(
                name='6', last_name='6',
                password=hash('6'), email='6@6.com', is_admin=False
            )

            user7 = User(
                name='7', last_name='7',
                password=hash('7'), email='7@7.com', is_admin=False
            )

            user8 = User(
                name='8', last_name='8',
                password=hash('8'), email='8@8.com', is_admin=False
            )

            user9 = User(
                name='9', last_name='9',
                password=hash('9'), email='9@9.com', is_admin=False
            )

            user10 = User(
                name='10', last_name='10',
                password=hash('10'), email='10@10.com', is_admin=False
            )

            user11 = User(
                name='11', last_name='11',
                password=hash('11'), email='11@11.com', is_admin=False
            )

            db.session.add_all([admin, default_user, user1, user2, user3, user4,
                               user5, user6, user7, user8, user9, user10, user11])
            db.session.commit()
