import yfinance as yf
import pandas as pd
import requests

# --- Patch Render/Yahoo: forcer headers sur chaque requête ----

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/plain,*/*"
})


def calcul_dca(ticker: str, montant: float, start: str):

    # --- Télécharger les données en forçant la Session (bypass Cloudflare) ---
    try:
        data = yf.download(
            ticker,
            start=start,
            progress=False,
            auto_adjust=True,
            threads=False,
            session=session      # ⭐ PATCH CRUCIAL
        )
    except Exception as e:
        return {"error": f"Erreur Yahoo Finance : {str(e)}"}

    # Vérifier résultat
    if data is None or data.empty:
        return {"error": f"Ticker '{ticker}' introuvable ou bloqué par Yahoo"}

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
