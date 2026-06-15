import pandas as pd
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson import ObjectId
import os

from train import predict_next_month

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db     = client.get_default_database()

CATEGORIES = [
    "food", "travel", "shopping", "education",
    "utilities", "entertainment", "healthcare",
    "government", "personal_care", "other"
]

# ─── GLOBAL AVG (dynamic, true monthly avg) ───────
def compute_global_avg():
    NUM_USERS = 50
    pipeline = [
        {"$match": {"transaction_direction": "Debit"}},
        {
            "$group": {
                "_id": {
                    "category": "$category",
                    "month"   : "$transaction_date"
                },
                "monthly_total": {"$sum": "$transaction_amount"}
            }
        },
        {
            "$group": {
                "_id"        : "$_id.category",
                "avg_monthly": {"$avg": "$monthly_total"}
            }
        }
    ]
    results    = db.transactions.aggregate(pipeline)
    global_avg = {}
    for r in results:
        if r["_id"] is None or r["_id"] == "":
            continue
        # divide by user count → per user monthly avg
        global_avg[r["_id"]] = round(r["avg_monthly"] / NUM_USERS, 2)
    return global_avg

GLOBAL_AVG = compute_global_avg()
print("\n=== GLOBAL AVG ===")
for cat, val in GLOBAL_AVG.items():
    print(f"  {cat}: ₹{val:,.2f}")

# ─── MAIN ML FUNCTION ─────────────────────────────
def calculate_ml_percentages(customer_id: str, goal_id: str):

    # ─── FETCH GOAL ───────────────────────────────
    goal = db.goals.find_one({"_id": ObjectId(goal_id)})
    if not goal:
        print("Goal not found.")
        return

    target_amount = float(goal["target_amount"])
    saved_amount  = float(goal.get("saved_amount", 0))
    target_date   = goal["target_date"]

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    # ─── GOAL ALREADY ACHIEVED ────────────────────
    remaining = target_amount - saved_amount
    if remaining <= 0:
        print("Goal already achieved.")
        db.goals.update_one(
            {"_id": ObjectId(goal_id)},
            {"$set": {"completed": True}}
        )
        return

    # ─── MONTHS LEFT ──────────────────────────────
    today       = datetime(2024, 1, 1)
    delta       = relativedelta(target_date, today)
    months_left = delta.years * 12 + delta.months
    if delta.days > 0:
        months_left += 1

    if months_left <= 0:
        print("Goal date already passed.")
        return

    monthly_need = remaining / months_left

    # ─── FETCH TRANSACTIONS ───────────────────────
    transactions = list(db.transactions.find({
        "customer_id": customer_id
    }))

    # ─── PREDICT SPEND PER CATEGORY ───────────────
    predicted_spend = {}
    for cat in CATEGORIES:
        predicted = predict_next_month(
            transactions,
            cat,
            cap=GLOBAL_AVG.get(cat, 500) * 3
        )
        if predicted is None or predicted <= 0:
            predicted_spend[cat] = GLOBAL_AVG.get(cat, 500)
        else:
            predicted_spend[cat] = predicted

    total_predicted = sum(predicted_spend.values())

    if total_predicted == 0:
        print("No spending data found.")
        return
    print("\n=== PREDICTED SPEND ===")
    for cat, val in predicted_spend.items():
        print(f"  {cat}: ₹{round(val, 2):,.2f}")
    print(f"  Total: ₹{sum(predicted_spend.values()):,.2f}")

    # ─── FLAT TAX ─────────────────────────────────
    flat_tax = round(
        min((monthly_need / total_predicted) * 100, 50), 2
    )

    # ─── TAX % PER CATEGORY (stable formula) ──────
    # high spend category → contributes more
    # low spend category  → contributes less
    # prediction actually influences output
    percentages = {}
    for cat in CATEGORIES:
        weight      = predicted_spend[cat] / total_predicted
        tax_percent = flat_tax * weight * len(CATEGORIES)
        percentages[cat] = round(min(tax_percent, 50), 2)

    # ─── PROJECTION (capped at monthly_need) ──────
    projected_monthly = min(
        monthly_need,
        sum(
            predicted_spend[cat] * percentages[cat] / 100
            for cat in CATEGORIES
        )
    )
    projected_total = projected_monthly * months_left
    on_track        = projected_total >= remaining

    # ─── BUILD RECORD ─────────────────────────────
    ml_record = {
        "customer_id"      : customer_id,
        "goal_id"          : goal_id,
        "flat_tax_percent" : flat_tax,
        "on_track"         : on_track,
        "projected_savings": round(projected_total, 2),
        "monthly_need"     : round(monthly_need, 2),
        "months_left"      : months_left,
        "percentages"      : percentages,
        "user_changes"     : {cat: 0 for cat in CATEGORIES},
        "updated_at"       : today.strftime("%Y-%m-%d")
    }

    # ─── UPSERT INTO MONGODB ──────────────────────
    db.ml_percentages.update_one(
        {"customer_id": customer_id, "goal_id": goal_id},
        {"$set": ml_record},
        upsert=True
    )

    print(f"✅ ML done for {customer_id} goal {goal_id}")
    print(f"   Monthly need : ₹{monthly_need:,.2f}")
    print(f"   Months left  : {months_left}")
    print(f"   Flat tax     : {flat_tax}%")
    print(f"   On track     : {on_track}")
    print(f"   Projected    : ₹{projected_total:,.2f}")
    print(f"   Percentages  : {percentages}")

    return ml_record


if __name__ == "__main__":
    test_goal = {
        "customer_id"  : "SYN001",
        "name"         : "Goa Trip",
        "description"  : "Trip with friends",
        "target_amount": 15000,
        "saved_amount" : 0,
        "target_date"  : "2024-12-01"
    }

    result  = db.goals.insert_one(test_goal)
    goal_id = str(result.inserted_id)

    calculate_ml_percentages("SYN001", goal_id)
    client.close()