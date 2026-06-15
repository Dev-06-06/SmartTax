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
        }},
        {"$sort": {"total": -1}}  # highest spend first — better for Power BI bar charts
    ]
    result = list(db.transactions.aggregate(pipeline))
    return jsonify(result), 200

@insights_bp.route("/goals", methods=["GET"])
def goals():
    # Group by completion status
    pipeline = [
        {"$group": {
            "_id"       : "$completed",
            "count"     : {"$sum": 1},
            "avg_target": {"$avg": "$target_amount"},
            "avg_saved" : {"$avg": "$saved_amount"}
        }}
    ]
    summary = list(db.goals.aggregate(pipeline))

    # Total pooled savings across ALL users (Idea 3 — FD pool)
    pool = db.goals.aggregate([
        {"$group": {"_id": None, "total_pooled_savings": {"$sum": "$saved_amount"}}}
    ])
    pool_result = list(pool)
    total_pooled = pool_result[0]["total_pooled_savings"] if pool_result else 0

    # Off-track users from ml_percentages (Idea 1 — loan targeting)
    off_track_count = db.ml_percentages.count_documents({"on_track": False})
    on_track_count  = db.ml_percentages.count_documents({"on_track": True})

    return jsonify({
        "summary"            : summary,
        "total_pooled_savings": total_pooled,
        "off_track_users"    : off_track_count,
        "on_track_users"     : on_track_count
    }), 200

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
    # user_changes is a dict/map — don't unwind, just return flat per user+goal
    docs = list(db.ml_percentages.find({}, {
        "customer_id" : 1,
        "goal_id"     : 1,
        "user_changes": 1
    }))

    result = []
    for doc in docs:
        changes = doc.get("user_changes", {})
        # Find categories the user actually changed (non-zero)
        active_overrides = {k: v for k, v in changes.items() if v != 0}
        result.append({
            "customer_id"     : doc.get("customer_id"),
            "goal_id"         : str(doc.get("goal_id", "")),
            "active_overrides": active_overrides,
            "override_count"  : len(active_overrides)  # how many categories user touched
        })

    return jsonify(result), 200