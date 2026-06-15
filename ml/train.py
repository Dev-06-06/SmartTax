import pandas as pd
from prophet import Prophet

def predict_next_month(
    transactions: list,
    category: str,
    cap: float = None
) -> float:
    """
    Given user transactions for a category,
    predict next month's spend using Prophet.
    Returns predicted spend amount.
    """
    if not transactions:
        return None

    df = pd.DataFrame(transactions)

    if "category" not in df.columns:
        return None

    if "transaction_date" not in df.columns:
        return None

    if "transaction_direction" not in df.columns:
        return None

    if "transaction_amount" not in df.columns:
        return None

    df = df[df["category"] == category].copy()

    if df.empty:
        return None

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    )
    df = df[df["transaction_date"].notna()].copy()

    if df.empty:
        return None

    # aggregate monthly spend
    monthly = (
        df[df["transaction_direction"] == "Debit"]
        .groupby(df["transaction_date"].dt.to_period("M"))["transaction_amount"]
        .sum()
        .reset_index()
    )
    monthly.columns = ["ds", "y"]
    monthly["ds"] = monthly["ds"].dt.to_timestamp()

    # prophet needs min 2 datapoints
    if len(monthly) < 2:
        return None  # fallback to global avg

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(monthly)

    # predict next month
    future = model.make_future_dataframe(periods=1, freq="ME")
    forecast = model.predict(future)

    predicted = forecast.iloc[-1]["yhat"]
    predicted = max(float(predicted), 0)  # no negative spend
    if cap is not None:
        predicted = min(predicted, cap)
    return predicted