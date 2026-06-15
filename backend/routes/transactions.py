from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
from datetime import datetime

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/", methods=["POST"])
def add_transaction():
    data        = request.json
    customer_id = data["customer_id"]
    amount      = data["amount"]
    category    = data["category"]
    taxes       = data.get("taxes_applied", [])

    # build transaction
    txn = {
        "customer_id"          : customer_id,
        "transaction_date"     : datetime.today().strftime("%Y-%m-%d"),
        "transaction_time"     : datetime.today().strftime("%H:%M"),
        "transaction_amount"   : amount,
        "transaction_direction": "Debit",
        "category"             : category,
        "transaction_type"     : "UPI",
        "account_type"         : "Savings",
        "account_balance"      : 0,
        "taxes_applied"        : taxes
    }

    db.transactions.insert_one(txn)

    # update saved_amount for each selected tax
    for tax in taxes:
        if tax.get("user_selected"):
            goal_id    = tax["goal_id"]
            percent    = tax["percent"]
            tax_amount = amount * percent / 100

            db.goals.update_one(
                {"_id": ObjectId(goal_id)},
                {"$inc": {"saved_amount": tax_amount}}
            )

    return jsonify({"message": "Transaction saved"}), 201

@transactions_bp.route("/<customer_id>", methods=["GET"])
def get_transactions(customer_id):
    txns = list(db.transactions.find(
        {"customer_id": customer_id},
        sort=[("transaction_date", -1)]
    ))
    for t in txns:
        t["_id"] = str(t["_id"])
    return jsonify(txns), 200