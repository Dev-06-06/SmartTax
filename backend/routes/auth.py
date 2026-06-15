from flask import Blueprint, request, jsonify
from db import db
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

def generate_token(customer_id):
    payload = {
        "customer_id": customer_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.json
    email    = data.get("email")
    password = data.get("password")
    name     = data.get("name")

    if db.auth.find_one({"email": email}):
        return jsonify({"error": "Email exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    result = db.auth.insert_one({
        "name"    : name,
        "email"   : email,
        "password": hashed,
    })

    customer_id = str(result.inserted_id)
    token       = generate_token(customer_id)

    return jsonify({"token": token, "customer_id": customer_id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.json
    email    = data.get("email")
    password = data.get("password")

    user = db.auth.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify({"error": "Wrong password"}), 401

    token = generate_token(str(user["_id"]))
    return jsonify({
        "token"      : token,
        "customer_id": str(user["_id"])
    }), 200