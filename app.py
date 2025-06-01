import os
from typing import Optional

from flask import (Flask, jsonify, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_cors import CORS
from flask_login import LoginManager

from services import admin_bp, auth_bp, chat_bp, sql_bp
from services.sql import init_sql
from services.sql.models import User

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.config.update(
    SECRET_KEY=os.environ.get('APP_SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('PYTHONANYWHERE_DB', 'sqlite:///db.sqlite'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_POOL_RECYCLE=280
)
CORS(app)

init_sql(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@login_manager.unauthorized_handler
def handle_unauthorized():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if best == 'application/json':
        return jsonify({'error': 'unauthorized'}), 401
    return redirect(url_for('auth.login', next=request.url))


@app.context_processor
def set_context_variables():
    return {'GOOGLE_MAPS_API_KEY': os.environ.get('GOOGLE_MAPS_API_KEY')}


@login_manager.user_loader
def load_user(user_id: str):
    user: Optional[User] = User.query.filter_by(id=user_id).first()
    if user:
        return user
    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder, "images"), "tidelock_sin_fondo.png")


# ---------------- register blueprints ---------------- #
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(sql_bp, url_prefix="/sql")
app.register_blueprint(admin_bp, url_prefix="/admin")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
