import yfinance as yf
import pandas as pd
import requests


# --- Forcer des headers pour Render (bypass Cloudflare/Yahoo) ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/plain,*/*"
})


def calcul_dca(ticker: str, montant: float, start: str):

    # --- Méthode alternative : Ticker.history() (plus fiable que download() sur Render) ---
    try:
        t = yf.Ticker(ticker, session=session)

        data = t.history(
            start=start,
            auto_adjust=True,
            actions=False,     # évite les colonnes inutiles
        )

    except Exception as e:
        return {"error": f"Erreur Yahoo Finance : {str(e)}"}

    # Vérifications
    if data is None or data.empty:
        return {"error": f"Ticker '{ticker}' introuvable ou bloqué par Yahoo"}

    if "Close" not in data.columns:
        return {"error": f"Aucune donnée 'Close' disponible pour {ticker}"}

    close_prices = data["Close"]

    # --- DCA ---
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
        "ticker": ticker.upper(),
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(valeur_finale, 2),
        "gain": round(rendement, 2),
        "gain_pct": round((rendement / total_investi) * 100, 2),
        "historique": historique
    }
