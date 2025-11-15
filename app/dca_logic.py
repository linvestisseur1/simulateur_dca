import yfinance as yf
from yfinance import shared              # <-- IMPORT TRÈS IMPORTANT
import pandas as pd

# Patch Render / Cloudflare / Yahoo blocks
shared._requests_args['headers'] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json,text/plain,*/*'
}

def calcul_dca(ticker: str, montant: float, start: str):

    # Téléchargement des données (version compatible Render)
    data = yf.download(
        ticker,
        start=start,
        progress=False,
        threads=False,
        auto_adjust=True
    )

    if data.empty:
        return {"error": f"Ticker '{ticker}' introuvable ou bloqué par Yahoo"}

    # On utilise la colonne "Close"
    close_prices = data["Close"]

    total_investi = 0
    total_shares = 0
    historique = []

    for date, prix in close_prices.items():
        if pd.isna(prix):
            continue

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
    rendement = valeur_finale - total_investi

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(valeur_finale, 2),
        "gain": round(rendement, 2),
        "gain_pct": round((rendement / total_investi) * 100, 2),
        "historique": historique
    }