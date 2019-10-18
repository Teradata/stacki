import stack.django_env

from datetime import timedelta
from pathlib import Path

from django.contrib.auth import authenticate
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token


app = Flask(__name__)
app.config["SECRET_KEY"] = Path("/opt/stack/etc/jwt.secret").read_text()
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
jwt = JWTManager(app)


@app.route("/", methods=["POST"])
def token():
	if request.is_json:
		params = request.get_json()
		username = params.get("username")
		password = params.get("password")
	else:
		username = request.form.get("username")
		password = request.form.get("password")

	if not username:
		return jsonify({"error": "Missing username parameter"}), 400
	if not password:
		return jsonify({"error": "Missing password parameter"}), 400

	user = authenticate(username=username, password=password)
	if user is None:
		return jsonify({"error": "Bad username or password"}), 401

	if not user.is_superuser:
		return jsonify({"error": "Access restricted to admin users only"}), 403

	# Generate a token
	return jsonify({"token": create_access_token(identity=username)})
