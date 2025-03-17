from flask import Flask, request
from flask_cors import CORS
from services import get_response

app = Flask(__name__)
CORS(app)


@app.route("/completion")
def completion():
    data: dict = request.json
    message = data.get("message")
    if not message:
        return {"error": "missing message"}, 400

    return {"message": get_response(message)}


if __name__ == '__main__':
    app.run(debug=True, port=5000)
