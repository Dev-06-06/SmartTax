from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
import sys
import os

sys.path.append(os.path.abspath("../ml"))
from ml import calculate_ml_percentages

goals_bp = Blueprint("goals", __name__)

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@goals_bp.route("/<customer_id>", methods=["GET"])
def get_goals(customer_id):
    goals = list(db.goals.find({"customer_id": customer_id}))
    return jsonify([serialize(g) for g in goals]), 200

@goals_bp.route("/", methods=["POST"])
def create_goal():
    data = request.json
    result = db.goals.insert_one({
        "customer_id"  : data["customer_id"],
        "name"         : data["name"],
        "description"  : data.get("description", ""),
        "target_amount": float(data["target_amount"]),
        "target_date"  : data["target_date"],
        "saved_amount" : 0.0,
        "completed"    : False
    })
    goal_id = str(result.inserted_id)

    # trigger ML
    calculate_ml_percentages(data["customer_id"], goal_id)

    return jsonify({"goal_id": goal_id}), 201

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    data = request.json
    db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": {
            "target_amount": data["target_amount"],
            "target_date"  : data["target_date"]
        }}
    )

    # recalculate ML on goal update
    goal = db.goals.find_one({"_id": ObjectId(goal_id)})
    calculate_ml_percentages(goal["customer_id"], goal_id)

    return jsonify({"message": "Goal updated"}), 200