# SmartTax

> Goal-driven fintech platform that transforms everyday UPI transactions into automated micro-savings using machine learning-powered tax recommendations.



## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Data Pipeline](#data-pipeline)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [API Reference](#api-reference)
- [Screenshots](#screenshots)
- [Business Intelligence Dashboards](#business-intelligence-dashboards)
- [Strategic Value for Banks](#strategic-value-for-banks)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

---

## Overview

SmartTax is a fintech prototype that helps users achieve financial goals through automated micro-savings.

Whenever a user performs a UPI transaction, SmartTax recommends category-specific "tax" percentages that get redirected toward savings goals such as:

- Emergency Fund
- Travel
- Education
- Investments
- Gadget Purchases

The platform combines Data Engineering (ETL), Machine Learning, REST APIs, Business Intelligence, and Financial Analytics to power two experiences:

| Side | Purpose |
|------|---------|
| **User Side** | Personal financial planning and savings optimization |
| **Bank Side** | Customer behavior analytics and BI dashboards |

---

## Problem Statement

**Users struggle to:**
- Save consistently
- Allocate money toward goals
- Understand spending patterns
- Build financial discipline

**Banks have limited visibility into:**
- Customer savings behavior
- Goal completion patterns
- Spending segments
- Financial engagement

SmartTax addresses both challenges through predictive analytics and goal-driven saving recommendations.

---

## Architecture

```text
┌─────────────────────────────────────────┐
│              DATA LAYER                  │
│  Kaggle CSV → ETL (Python/pandas)        │
│  → MongoDB Atlas                         │
│  Collections: users, transactions,       │
│  categories, goals, ml_percentages       │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│              ML LAYER                    │
│  Prophet → predict next month spend      │
│  KMeans  → segment users (BI only)       │
│  Formula → calculate tax % per category  │
│  Output  → ml_percentages collection     │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│            BACKEND LAYER                 │
│  Flask (Python)                          │
│  → Auth, Goals, Transactions             │
│  → Triggers ML on goal create/update     │
│  → Serves /api/insights for Power BI     │
└─────────────────────────────────────────┘
          ↓                  ↓
┌───────────────┐  ┌──────────────────────┐
│  USER SYSTEM  │  │     BANK SYSTEM       │
│  React + Vite │  │  Power BI Desktop     │
│  Login        │  │  → /api/insights      │
│  Dashboard    │  │  → Published Online   │
│  Transactions │  │  → Executive Reports  │
└───────────────┘  └──────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---------|------------|
| Dataset | Kaggle Banking Dataset |
| ETL | Python, Pandas |
| Database | MongoDB Atlas |
| ML Forecasting | Prophet |
| User Segmentation | KMeans |
| Backend | Flask |
| Frontend | React + Vite |
| BI | Power BI |


---

## Data Pipeline

### Step 1 — ETL

Raw banking transactions are cleaned and transformed via data cleaning, category standardization, user aggregation, and synthetic user generation.

**Output:**
```text
50 synthetic users
7601 transactions
MongoDB Atlas
```

### Step 2 — User Segmentation

KMeans clustering groups customers into **Conservative**, **Moderate**, and **Aggressive** segments using total spend, average transaction, transaction count, spending diversity, and spending variability.

Used exclusively for Business Intelligence, customer analytics, and bank dashboards.

### Step 3 — Goal Creation

A user creates a savings goal, which automatically triggers the ML engine.

```text
Laptop Fund
Target: ₹50,000
Duration: 12 months
```

### Step 4 — Spending Forecast

Prophet predicts next-month spending across categories.

```text
Food         ₹4,500
Shopping     ₹2,000
Travel       ₹1,500
Healthcare   ₹1,000
```

### Step 5 — Tax Percentage Generation

SmartTax calculates category-wise tax percentages required to achieve the goal, stored in the `ml_percentages` collection.

| Category | Predicted Spend | Recommended Tax |
|-----------|---------------|------------------|
| Food | ₹4,500 | 6% |
| Shopping | ₹2,000 | 12% |
| Travel | ₹1,500 | 10% |

### Step 6 — Transaction Processing

```text
Food Transaction: ₹500
Tax = ₹500 × 6% = ₹30
```

The user may accept, modify, or disable the recommendation. Accepted savings are added directly toward goal progress.

---

## Machine Learning Pipeline

### Forecasting Model — Prophet

| | |
|---|---|
| **Used for** | Monthly spending prediction, category-wise forecasting, savings planning |
| **Input** | Historical transactions, goal details |
| **Output** | Predicted spend, goal feasibility, tax percentages |

### Segmentation Model — KMeans Clustering

Used for behavioral segmentation, spending pattern analysis, and Business Intelligence.

| Segment | Characteristics |
|---------|------------------|
| Conservative | Lower spending, stable patterns |
| Moderate | Balanced spending |
| Aggressive | High spending, high variability |

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
POST /api/goals
PUT  /api/goals/<goal_id>
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

### Business Intelligence
```http
GET /api/insights/spending
GET /api/insights/goals
GET /api/insights/users
GET /api/insights/overrides
```

---


## Business Intelligence Dashboards

SmartTax includes a separate analytics platform designed for banks and financial institutions.

### Report 1 — Spending Analytics

![Spending Analytics](https://github.com/user-attachments/assets/fc7067de-c5c1-4f7e-81b8-0a8f1c5a3663)

**What banks can learn:** most popular spending categories, highest-value categories, customer transaction behavior, revenue opportunities, and seasonal spending trends.

**Business use case:** identify categories suitable for cashback campaigns, co-branded partnerships, and merchant promotions.

### Report 2 — Customer Segmentation

![Customer Segmentation](https://github.com/user-attachments/assets/e60d081a-f8f6-40c6-a936-78215e1fb5cc)

**What banks can learn:** distribution of customer segments, spending intensity, behavioral differences.

**Business use case:** create premium offers for aggressive users, savings plans for conservative users, and personalized engagement campaigns.

### Report 3 — Goal Analytics

![Goal Analytics](https://github.com/user-attachments/assets/a1c61c69-210d-4cd7-80f5-8c06820ed441)

**What banks can learn:** goal completion rates, savings behavior, on-track vs off-track customers.

**Business use case:** identify customers who may benefit from savings nudges, automated recurring deposits, and financial planning products.

---

## Strategic Value for Banks

**Customer Retention** — Identify users likely to disengage from savings goals.

**Product Recommendations** — Fixed Deposits, Goal-based Savings Accounts, Recurring Deposits, Investment Products.

**Loan Targeting** — Off-track users may be suitable candidates for Education Loans, Personal Loans, and Consumer Financing.

**Behavioral Analytics** — Understand spending habits, savings discipline, and category preferences.

---

## Project Structure

```text
SmartTax/
│
├── etl/
│   └── etl.py
│
├── ml/
│   ├── ml.py
│   └── cluster.py
│
├── backend/
│   ├── routes/
│   ├── models/
│   └── app.py
│
├── frontend/
│
├── powerbi/
│   └── SmartTax.pbix
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

# ETL / ML pipeline
cd ../etl
python etl.py
cd ../ml
python ml.py
python cluster.py
```

> Configure your MongoDB Atlas connection string and any required environment variables before running the backend.

---

## Future Enhancements

- Real UPI Integration
- Open Banking APIs
- AI Financial Assistant
- Investment Recommendations
- Fraud Detection
- Credit Risk Scoring
- Real-Time Analytics

---

## Contributors

**Dev**
B.Tech Computer Science & Engineering
FinTech • Data Analytics • Machine Learning • Business Intelligence

[GitHub](https://github.com/Dev-06-06) · [Repository](https://github.com/Dev-06-06/SmartTax)
