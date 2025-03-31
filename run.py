import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from services import get_response

app = Flask(__name__, template_folder="/frontend/templates")
app.config.update(
    SECRET_KEY=os.environ.get('APP_SECRET_KEY'),
)
CORS(app)


@app.route("/")
def home():
    return render_template("layout.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/completion", methods=["POST"])
def completion():
    data: dict = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "missing message"}), 400

    return jsonify({"message": get_response(message)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
