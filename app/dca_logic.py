# app/dca_logic.py
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Optional, Tuple, Dict, Any


def fetch_monthly_prices(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """
    Récupère l'historique mensuel via yfinance.
    Retourne un DataFrame avec colonnes : date, close
    """
    try:
        ticker = yf.Ticker(symbol)
        # Données mensuelles sur toute l'historique dispo
        hist = ticker.history(period="max", interval="1mo")

        if hist.empty:
            return None, {"message": f"Aucune donnée trouvée pour {symbol}"}

        # On ne garde que la date et le cours de clôture
        hist = hist.reset_index()[["Date", "Close"]]
        hist.columns = ["date", "close"]
        hist["date"] = pd.to_datetime(hist["date"]).dt.date
        hist = hist.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)

        return hist, None

    except Exception as e:
        return None, {"message": f"Erreur yfinance : {e}"}


def calcul_dca(symbol: str, amount: float = 100.0, start: Optional[str] = None):
    """
    Calcule un DCA mensuel fixe (amount) sur tout l'historique,
    ou à partir de la date 'start' (YYYY-MM-DD) si fournie.
    """
    df, error = fetch_monthly_prices(symbol)
    if error:
        return None, error

    # Filtre sur la date de départ si fournie
    if start:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            df = df[df["date"] >= start_date]
        except Exception:
            return None, {"message": "Format de date invalide (YYYY-MM-DD)"}

    if df.empty:
        return None, {"message": "Pas assez de données après filtrage."}

    total_invested = 0.0
    total_shares = 0.0
    rows = []

    for _, row in df.iterrows():
        price = float(row["close"])
        if price <= 0:
            # On saute les valeurs aberrantes
            continue

        shares_bought = amount / price
        total_shares += shares_bought
        total_invested += amount
        value = total_shares * price
        gain = value - total_invested
        pct = (gain / total_invested) * 100 if total_invested > 0 else 0.0

        rows.append({
            "date": row["date"].isoformat(),
            "price": price,
            "shares": total_shares,
            "invested": total_invested,
            "value": value,
            "gain": gain,
            "gain_pct": pct
        })

    if not rows:
        return None, {"message": "Impossible de calculer le DCA sur ces données."}

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
