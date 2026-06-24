# SmartTax

> **A two-sided fintech intelligence platform** — a behavioral nudge engine for users, and a monetization analytics layer for banks.
>
> SmartTax models how financial institutions can extract actionable signals from customer savings behavior: Prophet forecasts category-level spend, KMeans segments risk appetite, and Power BI surfaces partnership triggers for travel/telecom tie-ups and pre-approved loan targeting.

<table>
<tr>
<td align="center">
<img src="https://github.com/user-attachments/assets/fc7067de-c5c1-4f7e-81b8-0a8f1c5a3663" width="250"><br>
<b>Spending Analytics</b>
</td>
<td align="center">
<img src="https://github.com/user-attachments/assets/0c57057b-611b-4bdc-8776-edadca40f89c" width="250"><br>
<b>Customer Segmentation</b>
</td>
<td align="center">
<img src="https://github.com/user-attachments/assets/a1c61c69-210d-4cd7-80f5-8c06820ed441" width="250"><br>
<b>Goal Analytics</b>
</td>
</tr>
</table>

---

## Table of Contents

- [What SmartTax Actually Is](#what-smarttax-actually-is)
- [The Problem Worth Solving](#the-problem-worth-solving)
- [Platform Architecture](#platform-architecture)
- [Technology Stack](#technology-stack)
- [Data Engineering Pipeline](#data-engineering-pipeline)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [API Reference](#api-reference)
- [Business Intelligence Layer](#business-intelligence-layer)
- [Strategic Value for Banks](#strategic-value-for-banks)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

---

## What SmartTax Actually Is

SmartTax is not a savings app. It is a **dual-stakeholder fintech platform** designed around one core insight:

> *Every UPI transaction is a behavioral signal. Most banks ignore it. SmartTax doesn't.*

### Two Engines, One Platform

| Stakeholder | Engine | What It Does |
|-------------|--------|--------------|
| **User** | Behavioral Nudge Engine | Goal creation triggers ML → Prophet forecasts spend → micro-tax % is calculated per category → user is nudged to save with every transaction |
| **Bank** | BI Intelligence Layer | KMeans segments customers by risk appetite → Power BI surfaces partnership triggers, churn signals, and pre-approved loan candidates |

The user-facing side solves financial discipline. The bank-facing side solves customer monetization. Both are powered by the same underlying data pipeline — which is the architectural bet that makes this interesting.

---

## The Problem Worth Solving

**For users:**

Most people don't fail to save because they lack intention. They fail because the gap between *deciding to save* and *actually saving* is never bridged. There's no mechanism that converts a ₹500 Zomato order into ₹30 toward a laptop fund — automatically, contextually, without friction.

**For banks:**

A customer completes 200 UPI transactions. The bank records them. That's it. No behavioral segmentation. No spend forecasting. No signal that this customer is 3 months away from completing a ₹50,000 savings goal — and therefore primed for a fixed deposit upsell. The data exists. The intelligence doesn't.

SmartTax bridges both gaps.

---

## Platform Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                      DATA LAYER                           │
│  Kaggle Banking CSV → ETL (Python/pandas)                 │
│  → MongoDB Atlas                                          │
│  Collections: users, transactions, categories,            │
│               goals, ml_percentages                       │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                       ML LAYER                            │
│  Prophet     → time-series spend forecasting per category │
│  KMeans      → risk-appetite segmentation (BI only)       │
│  Tax Formula → category-wise % required to hit goal       │
│  Output      → ml_percentages collection                  │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                          │
│  Flask (Python)                                           │
│  → Auth, Goals, Transactions                              │
│  → Triggers ML pipeline on goal create/update             │
│  → Serves /api/insights endpoints for Power BI            │
└──────────────────────────────────────────────────────────┘
             ↓                            ↓
┌────────────────────┐       ┌────────────────────────────┐
│    USER SYSTEM     │       │       BANK SYSTEM           │
│  React + Vite      │       │  Power BI Desktop           │
│  ─────────────     │       │  ────────────────           │
│  Login / Register  │       │  Pulls from /api/insights   │
│  Goal Dashboard    │       │  Segmentation Reports       │
│  Transaction Feed  │       │  Goal Completion Analytics  │
│  Tax Recommendations│      │  Partnership Trigger Signals│
└────────────────────┘       └────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Why This Choice |
|-------|------------|-----------------|
| Dataset | Kaggle Banking Dataset | Real transaction distribution patterns |
| ETL | Python, Pandas | Flexible transformation with audit trail |
| Database | MongoDB Atlas | Schema-flexible for evolving goal/category structures |
| ML Forecasting | Facebook Prophet | Handles seasonality and missing data without fine-tuning |
| User Segmentation | KMeans Clustering | Interpretable clusters map cleanly to BFSI segments |
| Backend | Flask | Lightweight REST layer; triggers ML on goal events |
| Frontend | React + Vite | Fast iteration, component-driven dashboard |
| BI | Power BI | Enterprise-grade reporting; REST connector to Flask |

---

## Data Engineering Pipeline

### Step 1 — ETL

Raw Kaggle banking transactions are cleaned, normalized, and enriched through:

- Data cleaning and null handling
- Merchant category standardization
- User-level aggregation
- Synthetic user generation to simulate a realistic customer base

**Pipeline output:**
```text
50 synthetic users
7,601 transactions
Loaded into MongoDB Atlas
```

### Step 2 — KMeans Segmentation (Bank-Side Only)

Customers are clustered into three behavioral segments using unsupervised learning across five behavioral features:

| Feature | Signal |
|---------|--------|
| Total spend | Absolute consumption level |
| Average transaction size | Ticket size preference |
| Transaction count | Engagement frequency |
| Spending diversity | Category spread |
| Spending variability | Behavioral consistency |

| Segment | Characteristics | Bank Opportunity |
|---------|-----------------|-----------------|
| **Conservative** | Low spend, stable patterns | Savings products, FDs |
| **Moderate** | Balanced behavior | Cross-sell insurance, SIPs |
| **Aggressive** | High spend, high variability | Premium cards, pre-approved loans |

### Step 3 — Goal Creation Triggers ML

When a user sets a savings goal, the ML pipeline fires automatically:

```text
Input:  Goal → "Laptop Fund | ₹50,000 | 12 months"
Output: Category-wise tax percentages stored in ml_percentages
```

### Step 4 — Spend Forecasting via Prophet

Prophet generates next-month spend predictions per category using the user's historical transaction data:

```text
Food         → ₹4,500 predicted
Shopping     → ₹2,000 predicted
Travel       → ₹1,500 predicted
Healthcare   → ₹1,000 predicted
```

Prophet is particularly well-suited here: it handles irregular UPI spending patterns, accommodates weekday/weekend seasonality, and doesn't require clean, gapless time series — exactly the conditions real banking data presents.

### Step 5 — Tax Percentage Calculation

SmartTax computes the category-wise contribution rate needed to hit the goal within the target duration:

| Category | Predicted Spend | Recommended Tax | Monthly Contribution |
|-----------|----------------|-----------------|----------------------|
| Food | ₹4,500 | 6% | ₹270 |
| Shopping | ₹2,000 | 12% | ₹240 |
| Travel | ₹1,500 | 10% | ₹150 |

The percentages are inversely weighted — categories with elastic demand (Shopping, Travel) absorb higher tax rates than necessities (Food, Healthcare).

### Step 6 — Transaction Processing

```text
Transaction: Food ₹500
Applied Tax: 6%
Diverted:    ₹30 → Laptop Fund
```

The user can accept, modify, or override any recommendation. Accepted amounts are directly credited to goal progress.

---

## Machine Learning Pipeline

### Forecasting — Prophet

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Category-level monthly spend prediction |
| **Input** | Historical transactions, goal target, duration |
| **Output** | Predicted spend per category, tax % per category, goal feasibility score |
| **Why Prophet** | Designed for business time series with trend shifts and seasonality; performs well on sparse data without hyperparameter tuning |

### Segmentation — KMeans Clustering

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Customer behavioral profiling for bank BI |
| **Input** | Aggregated user transaction features |
| **Output** | Conservative / Moderate / Aggressive segments |
| **Why KMeans** | Produces interpretable, discrete segments that map directly to BFSI product targeting logic |

---

## API Reference

### Authentication
```http
POST /api/auth/register
POST /api/auth/login
```

### Goals
```http
GET  /api/goals/<customer_id>
POST /api/goals                     # Triggers ML pipeline
PUT  /api/goals/<goal_id>           # Triggers ML recalculation
```

### Transactions
```http
POST /api/transactions
GET  /api/transactions/<customer_id>
```

### ML Recommendations
```http
GET /api/percentages/<customer_id>/<goal_id>
PUT /api/percentages/<customer_id>/<goal_id>
```

### Business Intelligence (Power BI Connector)
```http
GET /api/insights/spending     # Category-level spend aggregates
GET /api/insights/goals        # Goal completion rates, on-track vs off-track
GET /api/insights/users        # Segment distribution, behavioral profiles
GET /api/insights/overrides    # ML recommendation override patterns
```

---

## Business Intelligence Layer

SmartTax's bank-facing layer is not a dashboard bolted on at the end. It is a first-class product surface — a REST-fed Power BI reporting layer that converts behavioral transaction data into actionable bank intelligence.

### Report 1 — Spending Analytics

![Spending Analytics](https://github.com/user-attachments/assets/fc7067de-c5c1-4f7e-81b8-0a8f1c5a3663)

**Intelligence surfaced:**
- Highest-volume and highest-value transaction categories
- Category-level seasonality and trend signals
- Per-customer spending velocity

**Partnership triggers this unlocks:**
Travel spike detected → co-branded travel card offer
Electronics category dominant → EMI financing campaign
Food delivery dominant → cashback partnership with aggregators

---

### Report 2 — Customer Segmentation

![Customer Segmentation](https://github.com/user-attachments/assets/0c57057b-611b-4bdc-8776-edadca40f89c)

**Intelligence surfaced:**
- Segment distribution across the customer base
- Spending intensity by cluster
- Behavioral drift (customers moving between segments)

**Targeting logic this unlocks:**
Aggressive segment → pre-approved personal loan or credit limit increase
Conservative segment → FD/RD nudge campaigns
Moderate segment → SIP or insurance cross-sell

---

### Report 3 — Goal Analytics

![Goal Analytics](https://github.com/user-attachments/assets/a1c61c69-210d-4cd7-80f5-8c06820ed441)

**Intelligence surfaced:**
- Goal completion rates by category (Travel, Education, Emergency, etc.)
- On-track vs off-track customer distribution
- Override patterns (where users reject ML recommendations)

**Retention and product logic this unlocks:**
Off-track users → savings nudge or automated RD offer
Goal completion approaching → upsell to next savings product
High override rate → signals distrust; candidate for financial advisory outreach

---

## Strategic Value for Banks

SmartTax answers a question most banks don't know how to ask:

> *What does a customer's UPI history tell me about what to sell them next — and when?*

| Use Case | Signal | Action |
|----------|--------|--------|
| **Customer Retention** | Goal progress stalling | Proactive savings nudge or RD offer |
| **Loan Targeting** | Off-track goals + high spend variability | Pre-approved personal/education loan |
| **Product Cross-sell** | Goal completion near | FD, next-tier savings account |
| **Partnership Triggers** | Category spend spikes | Co-branded card or cashback tie-up |
| **Churn Prevention** | Declining transaction frequency | Re-engagement campaign |
| **Credit Risk Scoring** | Segment + savings consistency | Input signal for credit decisioning |

---

## Project Structure

```text
SmartTax/
│
├── etl/
│   └── etl.py                 # Kaggle → pandas → MongoDB pipeline
│
├── ml/
│   ├── ml.py                  # Prophet forecasting + tax % calculation
│   └── cluster.py             # KMeans segmentation
│
├── backend/
│   ├── routes/                # Auth, Goals, Transactions, Insights
│   ├── models/                # MongoDB schemas
│   └── app.py                 # Flask application entry point
│
├── frontend/                  # React + Vite user dashboard
│
├── powerbi/
│   └── SmartTax.pbix          # Power BI report (REST-connected to Flask)
│
└── README.md
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Dev-06-06/SmartTax.git
cd SmartTax

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd ../frontend
npm install
npm run dev

# Run ETL pipeline
cd ../etl
python etl.py

# Run ML pipeline
cd ../ml
python ml.py        # Prophet forecasting
python cluster.py   # KMeans segmentation
```

> **Before running:** configure your MongoDB Atlas connection string and required environment variables in the backend `.env` file.

---

## Future Enhancements

| Enhancement | Strategic Value |
|-------------|----------------|
| Real UPI Integration | Live behavioral data replaces synthetic dataset |
| Open Banking APIs | Multi-bank transaction aggregation |
| AI Financial Assistant | Conversational goal planning layer |
| Fraud Detection | Anomaly flagging on transaction patterns |
| Credit Risk Scoring | Savings behavior as a creditworthiness signal |
| Real-Time Streaming | Kafka-based pipeline for live BI updates |
| Recommendation Engine | Investment product matching by segment + goal |

---

## Contributors

**Dev**
B.Tech Computer Science & Engineering
FinTech · Data Engineering · Machine Learning · Business Intelligence

[GitHub](https://github.com/Dev-06-06) · [Repository](https://github.com/Dev-06-06/SmartTax)
