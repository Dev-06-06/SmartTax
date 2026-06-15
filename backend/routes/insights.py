from flask import Blueprint, jsonify
from db import db

insights_bp = Blueprint("insights", __name__)

@insights_bp.route("/spending", methods=["GET"])
def spending():
    pipeline = [
        {"$match": {"transaction_direction": "Debit"}},
        {"$group": {
            "_id"  : "$category",
            "total": {"$sum": "$transaction_amount"},
            "count": {"$sum": 1}
        }}
    ]
    result = list(db.transactions.aggregate(pipeline))
    return jsonify(result), 200

@insights_bp.route("/goals", methods=["GET"])
def goals():
    pipeline = [
        {"$group": {
            "_id"         : "$completed",
            "count"       : {"$sum": 1},
            "avg_target"  : {"$avg": "$target_amount"},
            "avg_saved"   : {"$avg": "$saved_amount"}
        }}
    ]
    result = list(db.goals.aggregate(pipeline))
    return jsonify(result), 200

@insights_bp.route("/users", methods=["GET"])
def users():
    users = list(db.users.find({}, {
        "customer_id"   : 1,
        "region"        : 1,
        "segment"       : 1,
        "income_bracket": 1,
        "occupation"    : 1,
        "age"           : 1,
        "_id"           : 0
    }))
    return jsonify(users), 200

@insights_bp.route("/overrides", methods=["GET"])
def overrides():
    pipeline = [
        {"$project": {"user_changes": 1, "customer_id": 1}},
        {"$unwind": {
            "path"                      : "$user_changes",
            "preserveNullAndEmptyArrays": True
        }}
    ]
    result = list(db.ml_percentages.aggregate(pipeline))
    for r in result:
        r["_id"] = str(r["_id"])
    return jsonify(result), 200