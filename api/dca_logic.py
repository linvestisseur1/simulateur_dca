import yfinance as yf
import pandas as pd

def calcul_dca(ticker: str, montant: float, start: str):
    data = yf.download(ticker, start=start)
    if data.empty:
        return {"error": "ticker introuvable"}

    data = data["Close"]

    shares = 0
    total_investi = 0

    monthly = data.resample("M").first()

    for price in monthly:
        if pd.isna(price):
            continue
        total_investi += montant
        shares += montant / price

    valeur_finale = shares * data.iloc[-1]

    return {
        "ticker": ticker,
        "total_investi": round(total_investi, 2),
        "portefeuille": round(valeur_finale, 2),
        "profit": round(valeur_finale - total_investi, 2)
    }
