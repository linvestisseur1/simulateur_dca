import os
import requests
import pandas as pd
from datetime import datetime


# Lecture de la clé TwelveData dans Render
TWELVEDATA_KEY = os.getenv("TWELVEDATA_KEY")


def fetch_data(ticker: str):
    """
    Récupère l'historique mensuel du ticker via TwelveData.
    Retourne un DataFrame indexé par date avec 'close'.
    """

    if not TWELVEDATA_KEY:
        return None, {"message": "TWELVEDATA_KEY manquante dans Render."}

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": ticker,
        "interval": "1month",
        "start_date": "1990-01-01",
        "apikey": TWELVEDATA_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=15)
    except Exception as e:
        return None, {"message": f"Erreur réseau TwelveData : {e}"}

    try:
        data = r.json()
    except:
        return None, {"message": "Réponse TwelveData non valide.", "raw": r.text[:300]}

    # Erreur API TwelveData
    if "status" in data and data["status"] == "error":
        return None, {"message": f"Erreur TwelveData : {data.get('message')}"}

    # Données introuvables
    if "values" not in data:
        return None, {
            "message": "Aucune donnée 'values' dans la réponse TwelveData.",
            "raw": data
        }

    # Construction DataFrame
    df = pd.DataFrame(data["values"])

    if "datetime" not in df or "close" not in df:
        return None, {"message": "Format inattendu TwelveData.", "raw": data}

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])

    df = df.set_index("datetime").sort_index()

    return df, None



def calcul_dca(ticker: str, montant: float, start: str):
    """
    Calcule un DCA mensuel à partir des données TwelveData.
    """

    df, err = fetch_data(ticker)

    # Erreur lors de la récupération des données
    if err is not None:
        return {"error": err["message"], "details": err.get("raw")}

    # Vérification date de départ
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return {"error": "Format start incorrect. Exemple : 2010-01-01"}

    # Filtrer les données
    df = df[df.index >= start_dt]

    if df.empty:
        return {"error": f"Aucune donnée pour {ticker} à partir de {start}"}

    # Calcul du DCA
    total_shares = 0.0
    total_investi = 0.0
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

    if not historique:
        return {"error": "Aucune donnée exploitable après filtrage."}

    valeur_finale = historique[-1]["valeur_total"]
    gain = round(valeur_finale - total_investi, 2)

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(valeur_finale, 2),
        "gain": gain,
        "gain_pct": round((gain / total_investi) * 100, 2),
        "historique": historique
    }
