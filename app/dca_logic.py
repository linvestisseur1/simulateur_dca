import os
import requests
import pandas as pd


RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def fetch_prices(ticker: str, start: str):
    """
    Télécharge les prix via l'API RapidAPI Yahoo Finance Timeseries.
    Convertit le résultat en DataFrame équivalent à yfinance.
    """

    if RAPIDAPI_KEY is None:
        return None, {"error": "RAPIDAPI_KEY non configuré dans Render"}

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-timeseries"

    querystring = {"symbol": ticker, "region": "US"}

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)

        if response.status_code != 200:
            return None, {"error": f"Erreur API RapidAPI: {response.status_code}"}

        data = response.json()

        # L'API renvoie un gros JSON avec des series
        prices = data.get("timeseries", [])

        if not prices:
            return None, {"error": f"Aucune donnée disponible pour {ticker}"}

        # On récupère la série 'close'
        closes = next(
            (item.get("values") for item in prices if item.get("type") == "close"),
            None
        )

        if closes is None:
            return None, {"error": f"Impossible de trouver les prix pour {ticker}"}

        # Convertir en DataFrame
        df = pd.DataFrame(closes)
        df["date"] = pd.to_datetime(df["datetime"], unit='s')
        df = df.set_index("date")
        df = df.rename(columns={"close": "Close"})

        return df, None

    except Exception as e:
        return None, {"error": f"Erreur RapidAPI : {str(e)}"}


def calcul_dca(ticker: str, montant: float, start: str):

    df, err = fetch_prices(ticker, start)
    if err:
        return err

    close_prices = df["Close"]

    total_investi = 0
    total_shares = 0
    historique = []

    for date, prix in close_prices.items():
        shares_achetees = montant / prix
        total_shares += shares_achetees
        total_investi += montant

        historique.append({
            "date": str(date.date()),
            "cours": round(prix, 2),
            "shares": float(shares_achetees),
            "investi_total": round(total_investi, 2),
            "valeur_total": round(total_shares * prix, 2)
        })

    valeur_finale = total_shares * close_prices.iloc[-1]
    gain = valeur_finale - total_investi

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(valeur_finale, 2),
        "gain": round(gain, 2),
        "gain_pct": round((gain / total_investi) * 100, 2),
        "historique": historique
    }
