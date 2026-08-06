from functools import wraps
from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import load_db, save_db

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route("/register", methods=["POST"])
def register():
    db = load_db()
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    db.setdefault("users", [])

    for u in db["users"]:
        if u["username"] == username:
            return jsonify({"error": "username already taken"}), 400

    new_user_id = len(db["users"]) + 1
    db["users"].append({
        "user_id": new_user_id,
        "username": username,
        "password_hash": generate_password_hash(password)
    })
    save_db(db)

    return jsonify({"user_id": new_user_id, "username": username}), 201


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    db = load_db()

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    username = data.get("username")
    password = data.get("password")

    for u in db.get("users", []):
        if u["username"] == username and check_password_hash(u["password_hash"], password):
            session["user_id"] = u["user_id"]
            if request.is_json:
                return jsonify({"message": "logged in", "user_id": u["user_id"]}), 200
            return redirect(url_for("index"))

    if request.is_json:
        return jsonify({"error": "invalid username or password"}), 401
    return render_template("login.html", error="Invalid username or password")