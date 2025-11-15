import requests
import pandas as pd
from datetime import datetime

def fetch_data(ticker, api_key):
    url = "https://yahoo-finance160.p.rapidapi.com/history"

    params = {
        "symbol": ticker,
        "interval": "1mo",
        "range": "max"
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "yahoo-finance160.p.rapidapi.com"
    }

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    if "prices" not in data:
        return None

    df = pd.DataFrame(data["prices"])
    df = df[["date", "close"]].dropna()

    df["date"] = pd.to_datetime(df["date"], unit="s")
    df = df.set_index("date").sort_index()

    return df


def calcul_dca(ticker: str, montant: float, start: str, api_key: str):
    df = fetch_data(ticker, api_key)
    if df is None:
        return {"error": "Données introuvables pour ce ticker."}

    df = df[df.index >= start]

    total_shares = 0
    total_investi = 0
    historique = []

    for date, row in df.iterrows():
        prix = float(row["close"])
        if prix <= 0:
            continue

        shares = montant / prix
        total_shares += shares
        total_investi += montant
        valeur_portefeuille = round(total_shares * prix, 2)

        historique.append({
            "date": date.strftime("%Y-%m-%d"),
            "cours": round(prix, 2),
            "shares": round(total_shares, 4),
            "investi_total": round(total_investi, 2),
            "valeur_total": valeur_portefeuille
        })

    valeur_finale = historique[-1]["valeur_total"]
    gain = valeur_finale - total_investi

    return {
        "ticker": ticker,
        "investi_total": total_investi,
        "valeur_finale": valeur_finale,
        "gain": gain,
        "historique": historique
    }
