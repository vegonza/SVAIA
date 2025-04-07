from flask import Blueprint, jsonify, render_template, request

from .completions import get_response

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
def index():
    return render_template("chat.html")


@chat_bp.route("/completion", methods=["POST"])
def completion():
    data: dict = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "missing message"}), 400

    return jsonify({"message": get_response(message)})
