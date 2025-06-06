from flask import Blueprint, Flask
from typeguard import typechecked

from .models import User, db
from .projects import projects_bp
from .users import users_bp
from ..auth.password_utils import hash

__all__ = ["projects_bp", "users_bp"]

sql_bp = Blueprint("sql", __name__)

sql_bp.register_blueprint(projects_bp, url_prefix="/projects")
sql_bp.register_blueprint(users_bp, url_prefix="/users")


@typechecked
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

            db.session.add_all([admin, default_user])
            db.session.commit()
