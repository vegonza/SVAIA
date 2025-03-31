from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from services import get_response

app = Flask(__name__, template_folder="../frontend")
CORS(app)


@app.route("/")
def home():
    return render_template("/home/index.html")


@app.route("/completion", methods=["POST"])
def completion():
    data: dict = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "missing message"}), 400

    return jsonify({"message": get_response(message)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
