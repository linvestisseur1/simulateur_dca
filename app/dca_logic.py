# app/dca_logic.py
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

TWELVEDATA_KEY = os.getenv("TWELVEDATA_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


def fetch_monthly_prices(symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """
    Récupère les prix mensuels via TwelveData pour un symbole donné.
    Retourne (df, error). Si error != None, df est None.
    df contient les colonnes: ['date', 'close'] triées par date ascendante.
    """
    if not TWELVEDATA_KEY:
        return None, {"message": "TWELVEDATA_KEY manquante sur le serveur."}

    params = {
        "symbol": symbol,
        "interval": "1month",
        "outputsize": 5000,  # max sensible
        "apikey": TWELVEDATA_KEY,
        "order": "asc",
        "format": "JSON",
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, {"message": f"Erreur de connexion à TwelveData : {e}"}

    data = resp.json()

    # Gestion des erreurs TwelveData
    if isinstance(data, dict) and data.get("status") == "error":
        return None, {"message": data.get("message", "Erreur renvoyée par TwelveData.")}

    values = data.get("values")
    if not values:
        return None, {"message": "Aucune donnée renvoyée par TwelveData pour ce symbole."}

    df = pd.DataFrame(values)

    if "datetime" not in df.columns or "close" not in df.columns:
        return None, {"message": "Format de données TwelveData inattendu (datetime/close manquant)."}

    # Conversion types + tri
    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)

    if df.empty:
        return None, {"message": "Données vides après nettoyage."}

    return df[["date", "close"]], None


def calcul_dca(symbol: str, amount: float = 100.0, start: Optional[str] = None):
    """
    Calcule un DCA mensuel sur le symbole donné :
    - amount : montant investi chaque mois
    - start : date de début au format 'YYYY-MM-DD' (optionnel)

    Retourne (result, error) où result est un dict prêt à être renvoyé en JSON.
    """
    df, error = fetch_monthly_prices(symbol)
    if error:
        return None, error

    # Filtre sur la date de début si fournie
    if start:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
        except ValueError:
            return None, {"message": "Format de date invalide. Utilise YYYY-MM-DD."}

        df = df[df["date"] >= start_date].reset_index(drop=True)

    if df.empty:
        return None, {"message": "Aucune donnée disponible sur la période demandée."}

    # Boucle DCA
    total_shares = 0.0
    total_invested = 0.0
    rows = []

    for _, row in df.iterrows():
        price = float(row["close"])
        if price <= 0:
            # on saute les valeurs bizarres
            continue

        bought = amount / price
        total_shares += bought
        total_invested += amount
        portfolio_value = total_shares * price
        gain = portfolio_value - total_invested
        gain_pct = (gain / total_invested) * 100 if total_invested > 0 else 0.0

        rows.append({
            "date": row["date"].isoformat(),
            "price": round(price, 4),
            "shares": round(total_shares, 6),
            "invested": round(total_invested, 2),
            "value": round(portfolio_value, 2),
            "gain": round(gain, 2),
            "gain_pct": round(gain_pct, 2),
        })

    if not rows:
        return None, {"message": "Impossible de calculer un DCA sur ces données."}

    last = rows[-1]

    result = {
        "symbol": symbol.upper(),
        "monthly_invest": float(amount),
        "start_date": rows[0]["date"],
        "end_date": rows[-1]["date"],
        "n_periods": len(rows),
        "total_invested": last["invested"],
        "current_value": last["value"],
        "total_gain": last["gain"],
        "total_gain_pct": last["gain_pct"],
        "data": rows,
    }

    return result, None
