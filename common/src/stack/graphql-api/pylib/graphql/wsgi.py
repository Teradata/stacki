import atexit
from datetime import timedelta
from functools import wraps
import importlib
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_jwt_extended import (
	JWTManager, create_access_token, decode_token,
	get_jwt_claims, get_jti, get_raw_jwt, jwt_required
)
from flask_jwt_extended.exceptions import NoAuthorizationError
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from stack.commands import get_mysql_connection
from stack.graphql import execute


# Set up the Flask app and JWT
app = Flask(__name__)
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
app.config["SECRET_KEY"] = Path("/opt/stack/etc/jwt.secret").read_text()
app.config["SESSION_COOKIE_PATH"] = "/api/graphql"
app.config["SESSION_COOKIE_SECURE"] = True
jwt = JWTManager(app)


def check_claims(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		claims = get_jwt_claims()
		jti = get_raw_jwt()["jti"]

		if claims.get("restricted") == "playground" and session.get("jti") != jti:
			# The token given was a playground one and it didn't match the session
			raise NoAuthorizationError("Provided token only works in playground session")

		return func(*args, **kwargs)
	return wrapper


@app.route("/", methods=["GET"])
def redirect_to_playground():
	return redirect(url_for("playground"))


@app.route("/", methods=["POST"])
@jwt_required
@check_claims
def graphql_endpoint():
	connection = get_mysql_connection()
	success, result = execute(connection, request.get_json())
	connection.close()

	return jsonify(result), 200 if success else 400


@app.route("/playground/", methods=["GET"])
def playground():
	# See if the login_token is in the session
	if "login_token" in session:
		# Validate the login_token
		login_token = decode_token(session.pop("login_token"))

		# Generate a new token, which lives 30 days, and is restricted to playground usage
		token = create_access_token(
			identity=login_token["identity"],
			expires_delta=timedelta(days=30),
			user_claims={"restricted": "playground"}
		)

		# Add the playground token jti to the session
		session["jti"] = get_jti(token)

		return render_template("playground.html", token=token)

	return redirect(url_for("login"))


@app.route("/playground/login/", methods=["GET", "POST"])
def login():
	error = None
	if request.method == 'POST':
		# Try to get a JWT token
		data = {
			"username": request.form.get("username", ""),
			"password": request.form.get("password", "")
		}

		token_data = requests.post(
			"https://localhost/api/token/",
			data=data,
			verify=False
		).json()

		if "token" in token_data:
			# Set the short-lived token in the session, to get exchanged for
			# a longer-lived playground only token
			session["login_token"] = token_data["token"]

			return redirect(url_for("playground"))
		elif "error" in token_data:
			error = token_data["error"]
		else:
			error = "Unknown failure to authenticate"

	return render_template("login.html", error=error)
