import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager

from services import auth_bp, chat_bp
from services.auth.test_users import users
from services.sql import init_sql

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.config.update(
    SECRET_KEY=os.environ.get('APP_SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
CORS(app)

init_sql(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id: str):
    for user in users.values():
        if user.id == int(user_id):
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
