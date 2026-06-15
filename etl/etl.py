import pandas as pd
from pymongo import MongoClient
import random
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI      = os.getenv("MONGO_URI")
CSV_PATH       = os.getenv("CSV_PATH")
NUM_SYNTHETIC  = 50
POOL_SIZE      = 10

client = MongoClient(MONGO_URI)
db     = client.get_default_database()

df = pd.read_csv(CSV_PATH)

keep_cols = [
    "customer_id", "transaction_date", "transaction_time",
    "transaction_amount", "transaction_direction",
    "account_type", "merchant_category", "state",
    "credit_score", "transaction_type", "account_balance"
]
df = df[keep_cols]

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

category_map = {
    "Food & Dining" : "food",
    "Education"     : "education",
    "Utilities"     : "utilities",
    "Travel"        : "travel",
    "Government"    : "government",
    "Entertainment" : "entertainment",
    "Healthcare"    : "healthcare",
    "Shopping"      : "shopping",
    "Retail"        : "shopping",
    "Personal Care" : "personal_care"
}
df["merchant_category"] = df["merchant_category"].map(
    category_map
).fillna("other")

occupations = [
    "salaried", "self-employed",
    "student", "business", "freelancer"
]

# ─── TOP 500 ACTIVE USERS ─────────────────────────
top_500 = (
    df["customer_id"]
    .value_counts()
    .head(NUM_SYNTHETIC * POOL_SIZE)
    .index.tolist()
)

df = df[df["customer_id"].isin(top_500)]

# ─── BUILD SYNTHETIC USERS + TRANSACTIONS ─────────
user_records        = []
transaction_records = []

for i in range(NUM_SYNTHETIC):
    pool    = top_500[i * POOL_SIZE : (i + 1) * POOL_SIZE]
    syn_id  = f"SYN{i+1:03d}"
    pool_df = df[df["customer_id"].isin(pool)]

    # income bracket
    avg_spend = pool_df[
        pool_df["transaction_direction"] == "Debit"
    ]["transaction_amount"].mean()

    if avg_spend < 5000:
        income_bracket = "low"
    elif avg_spend < 20000:
        income_bracket = "mid"
    else:
        income_bracket = "high"

    # user profile = average/mode of pool
    user_records.append({
        "customer_id"   : syn_id,
        "age"           : random.randint(18, 60),
        "occupation"    : random.choice(occupations),
        "region"        : pool_df["state"].mode()[0],
        "account_type"  : pool_df["account_type"].mode()[0],
        "credit_score"  : int(pool_df["credit_score"].mean()),
        "income_bracket": income_bracket
    })

    # transactions remapped to synthetic id
    for _, row in pool_df.iterrows():
        transaction_records.append({
            "customer_id"          : syn_id,
            "transaction_date"     : row["transaction_date"].strftime("%Y-%m-%d"),
            "transaction_time"     : row["transaction_time"],
            "transaction_amount"   : float(row["transaction_amount"]),
            "transaction_direction": row["transaction_direction"],
            "account_type"         : row["account_type"],
            "category"             : row["merchant_category"],
            "transaction_type"     : row["transaction_type"],
            "account_balance"      : float(row["account_balance"])
        })

# ─── CATEGORIES ───────────────────────────────────
unique_categories = list({t["category"] for t in transaction_records})
category_records  = [{"name": c} for c in unique_categories]

# ─── INSERT INTO MONGODB ──────────────────────────
db.users.drop()
db.transactions.drop()
db.categories.drop()

db.users.insert_many(user_records)
print(f"✅ Users inserted: {len(user_records)}")

db.transactions.insert_many(transaction_records)
print(f"✅ Transactions inserted: {len(transaction_records)}")

db.categories.insert_many(category_records)
print(f"✅ Categories inserted: {len(category_records)}")

# ─── INDEXES ──────────────────────────────────────
db.users.create_index("customer_id", unique=True)
db.transactions.create_index("customer_id")
db.transactions.create_index("category")
db.transactions.create_index(
    [("customer_id", 1), ("category", 1)]
)

print("✅ ETL complete. Indexes created.")
client.close()