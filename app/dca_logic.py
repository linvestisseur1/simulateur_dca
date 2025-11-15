import requests
import pandas as pd
from datetime import datetime
import os

RAPID_KEY = os.getenv("RAPIDAPI_KEY")

def fetch_prices(ticker: str, start: str):
    """Appelle RapidAPI pour récupérer l'historique."""
    
    url = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/hi/history"

    query = {
        "symbol": ticker,
        "interval": "1d"
    }

    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    try:
        resp = requests.get(url, headers=headers, params=query, timeout=10)
    except Exception as e:
        return {"error": f"Erreur réseau RapidAPI : {str(e)}"}

    # 🔍 Si le serveur renvoie du texte, on l'affiche
    try:
        data = resp.json()
    except Exception:
        return {"error": f"Réponse non-JSON de RapidAPI : {resp.text}"}

    # 🔍 Vérifier la structure
    if not isinstance(data, dict):
        return {"error": f"RapidAPI a renvoyé quelque chose d'inattendu : {data}"}

    if "items" not in data:
        return {"error": f"Pas de données 'items' dans RapidAPI : {data}"}

    # Convertir en DataFrame
    df = pd.DataFrame(data["items"])
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= pd.to_datetime(start)]
    df = df.sort_values("date")

    if df.empty:
        return {"error": "Aucune donnée historique retournée"}

    return df


def calcul_dca(ticker: str, montant: float, start: str):

    prices = fetch_prices(ticker, start)

    if isinstance(prices, dict) and "error" in prices:
        return prices  # renvoie l'erreur proprement

    total_shares = 0
    total_investi = 0
    historique = []

    for _, row in prices.iterrows():
        price = row["close"]
        date = row["date"].date()

        if pd.isna(price): 
            continue

        shares = montant / price
        total_shares += shares
        total_investi += montant

        historique.append({
            "date": str(date),
            "cours": round(price, 2),
            "shares": float(shares),
            "investi_total": round(total_investi, 2),
            "valeur_total": round(total_shares * price, 2)
        })

    final_valeur = total_shares * prices.iloc[-1]["close"]

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(final_valeur, 2),
        "gain": round(final_valeur - total_investi, 2),
        "gain_pct": round(((final_valeur - total_investi) / total_investi) * 100, 2),
        "historique": historique
    }
