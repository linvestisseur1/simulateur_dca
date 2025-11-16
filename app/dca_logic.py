# app/dca_logic.py
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

TWELVEDATA_KEY = os.getenv("TWELVEDATA_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


def fetch_monthly_prices(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    if not TWELVEDATA_KEY:
        return None, {"message": "TWELVEDATA_KEY manquante sur le serveur."}

    params = {
        "symbol": symbol,
        "interval": "1month",
        "outputsize": 5000,
        "apikey": TWELVEDATA_KEY,
        "order": "asc",
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return None, {"message": f"Erreur TwelveData : {e}"}

    data = resp.json()
    if isinstance(data, dict) and data.get("status") == "error":
        return None, {"message": data.get("message")}

    if "values" not in data:
        return None, {"message": "Format TwelveData incorrect (pas de values)."}

    df = pd.DataFrame(data["values"])
    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"]).sort_values("date").reset_index()

    return df[["date", "close"]], None


def calcul_dca(symbol: str, amount: float = 100.0, start: Optional[str] = None):
    df, error = fetch_monthly_prices(symbol)
    if error:
        return None, error

    if start:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            df = df[df["date"] >= start_date]
        except:
            return None, {"message": "Format de date invalide (YYYY-MM-DD)"}

    total_invested = 0
    total_shares = 0
    rows = []

    for _, row in df.iterrows():
        price = float(row["close"])
        shares_bought = amount / price
        total_shares += shares_bought
        total_invested += amount
        value = total_shares * price
        gain = value - total_invested
        pct = (gain / total_invested) * 100

        rows.append({
            "date": row["date"].isoformat(),
            "price": price,
            "shares": total_shares,
            "invested": total_invested,
            "value": value,
            "gain": gain,
            "gain_pct": pct
        })

    last = rows[-1]
    result = {
        "symbol": symbol.upper(),
        "monthly_invest": amount,
        "start_date": rows[0]["date"],
        "end_date": rows[-1]["date"],
        "n_periods": len(rows),
        "total_invested": total_invested,
        "current_value": last["value"],
        "total_gain": last["gain"],
        "total_gain_pct": last["gain_pct"],
        "data": rows,
    }

    return result, None
