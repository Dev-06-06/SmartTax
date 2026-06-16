import json
import random
from datetime import datetime, timedelta

random.seed(42)

CATEGORIES  = ["food", "shopping", "utilities", "healthcare", "travel",
               "government", "education", "entertainment", "personal_care"]
REGIONS     = ["Maharashtra", "Karnataka", "Delhi", "Tamil Nadu",
               "Telangana", "Gujarat", "Rajasthan", "West Bengal"]
OCCUPATIONS = ["student", "salaried", "freelancer", "business", "self-employed"]
SEGMENTS    = ["conservative", "moderate", "aggressive"]
INCOMES     = ["low", "mid", "high"]
GOAL_NAMES  = ["Goa Trip", "New Laptop", "Emergency Fund", "Wedding",
               "Car Down Payment", "Europe Trip", "Home Renovation", "MBA Fund"]

BASE_SPEND = {
    "food"         : (300,  800),
    "shopping"     : (500,  3000),
    "utilities"    : (800,  5000),
    "healthcare"   : (500,  8000),
    "travel"       : (500,  6000),
    "government"   : (200,  2000),
    "education"    : (1000, 10000),
    "entertainment": (200,  1500),
    "personal_care": (200,  1000),
}

# Segment behavior multipliers — aggressive spends more
SEGMENT_MULTIPLIER = {
    "conservative": 0.7,
    "moderate"    : 1.0,
    "aggressive"  : 1.5
}

NUM_USERS = 200
START_DATE = datetime(2023, 1, 1)

# --- 1. USERS ---
users = []
for i in range(1, NUM_USERS + 1):
    users.append({
        "customer_id"   : f"SYN{i:03d}",
        "age"           : random.randint(21, 55),
        "occupation"    : random.choice(OCCUPATIONS),
        "region"        : random.choice(REGIONS),
        "income_bracket": random.choice(INCOMES),
        "segment"       : random.choices(
                            SEGMENTS,
                            weights=[0.5, 0.35, 0.15]
                          )[0]
    })

# --- 2. TRANSACTIONS (1 row per txn, with customer_id) ---
transactions = []
for user in users:
    multiplier = SEGMENT_MULTIPLIER[user["segment"]]
    for cat, (mn, mx) in BASE_SPEND.items():
        txn_count = random.randint(5, 30)
        for _ in range(txn_count):
            amount = round(random.uniform(mn, mx) * multiplier, 2)
            date   = START_DATE + timedelta(days=random.randint(0, 365))
            transactions.append({
                "customer_id"       : user["customer_id"],
                "category"          : cat,
                "amount"            : amount,
                "transaction_date"  : date.strftime("%Y-%m-%d"),
                "region"            : user["region"],   # denormalized for easier BI
                "segment"           : user["segment"],  # denormalized for easier BI
                "occupation"        : user["occupation"]
            })

# --- 3. GOALS (1 row per user) ---
goals = []
for user in users:
    target      = random.choice([5000, 10000, 15000, 20000, 25000, 50000])
    on_track    = random.random() < 0.7
    progress    = random.uniform(0.5, 1.2) if on_track else random.uniform(0.05, 0.45)
    saved       = round(min(target * progress, target), 2)
    completed   = saved >= target
    months_left = random.randint(1, 24)
    goal_name   = random.choice(GOAL_NAMES)

    goals.append({
        "customer_id"   : user["customer_id"],
        "region"        : user["region"],
        "segment"       : user["segment"],
        "occupation"    : user["occupation"],
        "income_bracket": user["income_bracket"],
        "goal_name"     : goal_name,
        "target_amount" : target,
        "saved_amount"  : saved,
        "completed"     : completed,
        "on_track"      : on_track,
        "months_left"   : months_left
    })

# --- 4. OVERRIDES (1 row per user) ---
overrides = []
for user in users:
    changes = {}
    if random.random() < 0.4:
        tweaked = random.sample(CATEGORIES, random.randint(1, 3))
        for cat in CATEGORIES:
            changes[cat] = random.randint(-5, 5) if cat in tweaked else 0
    else:
        changes = {cat: 0 for cat in CATEGORIES}

    overrides.append({
        "customer_id"  : user["customer_id"],
        "segment"      : user["segment"],
        "override_count": sum(1 for v in changes.values() if v != 0),
        **{f"override_{k}": v for k, v in changes.items()}
    })

# --- EXPORT ---
with open("users.json",        "w") as f: json.dump(users,        f, indent=2)
with open("transactions.json", "w") as f: json.dump(transactions, f, indent=2)
with open("goals.json",        "w") as f: json.dump(goals,        f, indent=2)
with open("overrides.json",    "w") as f: json.dump(overrides,    f, indent=2)

print(f"✅ Users       : {len(users)}")
print(f"✅ Transactions: {len(transactions)}")
print(f"✅ Goals       : {len(goals)}")
print(f"✅ Overrides   : {len(overrides)}")
print(f"✅ Pooled ₹    : {sum(g['saved_amount'] for g in goals):,.2f}")
print(f"✅ On Track    : {sum(1 for g in goals if g['on_track'])}")
print(f"✅ Off Track   : {sum(1 for g in goals if not g['on_track'])}")