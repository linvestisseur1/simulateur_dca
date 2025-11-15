import requests
import pandas as pd

API_KEY = "19441329421a43e78a1948f6e43db40b"  # <<< Remplace ici


def get_history(ticker, start):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": ticker,
        "interval": "1day",
        "apikey": API_KEY,
        "start_date": start,
        "order": "ASC"
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "values" not in data:
        return None

    # Converti JSON → DataFrame propre
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = df["close"].astype(float)
    df = df.sort_values("datetime")

    return df


def calcul_dca(ticker, montant, start):
    df = get_history(ticker, start)
    if df is None or df.empty:
        return {"error": f"Impossible de récupérer '{ticker}'"}

    total_shares = 0
    total_investi = 0
    historique = []

    for _, row in df.iterrows():
        prix = row["close"]
        date = row["datetime"].date()

        shares = montant / prix
        total_shares += shares
        total_investi += montant

        historique.append({
            "date": str(date),
            "cours": round(prix, 2),
            "shares": round(shares, 6),
            "investi_total": round(total_investi, 2),
            "valeur_total": round(total_shares * prix, 2)
        })

    valeur_finale = total_shares * df.iloc[-1]["close"]
    gain = valeur_finale - total_investi

    return {
        "ticker": ticker,
        "investi_total": total_investi,
        "valeur_finale": round(valeur_finale, 2),
        "gain": round(gain, 2),
        "gain_pct": round((gain / total_investi) * 100, 2),
        "historique": historique
    }
