from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId

percentages_bp = Blueprint("percentages", __name__)

@percentages_bp.route("/<customer_id>/<goal_id>", methods=["GET"])
def get_percentages(customer_id, goal_id):
    record = db.ml_percentages.find_one({
        "customer_id": customer_id,
        "goal_id"    : goal_id
    })
    if not record:
        return jsonify({"error": "Not found"}), 404

    record["_id"] = str(record["_id"])

    # apply user_changes
    effective = {}
    for cat, pct in record["percentages"].items():
        change            = record["user_changes"].get(cat, 0)
        effective[cat]    = round(pct + change, 2)

    record["effective_percentages"] = effective
    return jsonify(record), 200

@percentages_bp.route("/<customer_id>/<goal_id>", methods=["PUT"])
def update_user_change(customer_id, goal_id):
    data     = request.json
    category = data["category"]
    change   = data["change"]  # delta: -2, +3 etc

    db.ml_percentages.update_one(
        {"customer_id": customer_id, "goal_id": goal_id},
        {"$set": {f"user_changes.{category}": change}}
    )
    return jsonify({"message": "User change saved"}), 200