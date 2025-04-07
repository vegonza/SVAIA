import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from services import auth_bp, chat_bp

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.config.update(
    SECRET_KEY=os.environ.get('APP_SECRET_KEY'),
)
CORS(app)


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
