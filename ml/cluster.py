import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db     = client.get_default_database()

def segment_all_users():
    """
    KMeans on all 50 users.
    Segments: aggressive / moderate / conservative spender.
    Updates users collection with segment field.
    For BI use only.
    """
    users = list(db.users.find({}, {"customer_id": 1}))
    
    feature_rows = []
    customer_ids = []

    for user in users:
        cid = user["customer_id"]
        txns = list(db.transactions.find({
            "customer_id": cid,
            "transaction_direction": "Debit"
        }))

        if not txns:
            continue

        df = pd.DataFrame(txns)
        
        total_spend    = df["transaction_amount"].sum()
        avg_txn        = df["transaction_amount"].mean()
        txn_count      = len(df)
        unique_cats    = df["category"].nunique()
        spend_std      = df["transaction_amount"].std()

        feature_rows.append([
            total_spend, avg_txn,
            txn_count, unique_cats, spend_std
        ])
        customer_ids.append(cid)

    if len(feature_rows) < 3:
        return

    X = np.array(feature_rows)

    # normalize
    from sklearn.preprocessing import StandardScaler
    X_scaled = StandardScaler().fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # map cluster → segment name
    # find which cluster = highest avg spend
    cluster_spend = {}
    for i, label in enumerate(labels):
        cluster_spend.setdefault(label, []).append(feature_rows[i][0])

    cluster_avg = {k: np.mean(v) for k, v in cluster_spend.items()}
    sorted_clusters = sorted(cluster_avg, key=cluster_avg.get)

    segment_map = {
        sorted_clusters[0]: "conservative",
        sorted_clusters[1]: "moderate",
        sorted_clusters[2]: "aggressive"
    }

    # update users in MongoDB
    for cid, label in zip(customer_ids, labels):
        db.users.update_one(
            {"customer_id": cid},
            {"$set": {"segment": segment_map[label]}}
        )

    print("✅ KMeans segmentation complete.")
if __name__ == "__main__":
    segment_all_users()
    client.close()