import os
import requests
import pandas as pd


# ===============================
#  Fonction : récupération via RapidAPI (Yahu Financials)
# ===============================
def fetch_history_rapid(ticker: str, start: str):
    """
    Récupère les données journalières via Yahu Financials (RapidAPI)
    """

    url = "https://yahu-financials.p.rapidapi.com/v2/get-timeseries"

    headers = {
        "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "yahu-financials.p.rapidapi.com"
    }

    params = {
        "symbol": ticker,
        "interval": "1d"
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        return {"error": f"Erreur RapidAPI : {e}"}

    # Vérification contenu
    if not isinstance(data, dict):
        return {"error": f"Réponse RapidAPI inattendue : {data}"}

    if "items" not in data:
        return {"error": f"Pas de données 'items' dans RapidAPI : {data}"}

    items = data["items"]

    # Conversion en DataFrame
    df = pd.DataFrame(items)

    # Vérification colonnes essentielles
    if "close" not in df or "date" not in df:
        return {"error": f"Données RapidAPI incomplètes : colonnes manquantes dans {items}"}

    # Convert date to datetime + filtre start
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= pd.to_datetime(start)]
    df = df.sort_values("date")

    return df


# ===============================
#  Fonction : calcul du DCA
# ===============================
def calcul_dca(ticker: str, montant: float, start: str):
    """
    Calcul du DCA basé sur les données Yahu Financials via RapidAPI.
    """

    # ---- Récupération données ----
    df = fetch_history_rapid(ticker, start)

    if isinstance(df, dict) and "error" in df:
        return df  # renvoyer l'erreur proprement

    if df.empty:
        return {"error": f"Aucune donnée reçue pour {ticker}"}

    # ---- Calcul du DCA ----
    total_investi = 0
    total_shares = 0
    historique = []

    for _, row in df.iterrows():
        prix = float(row["close"])
        date = row["date"].date()

        shares_achetees = montant / prix

        total_investi += montant
        total_shares += shares_achetees

        historique.append({
            "date": str(date),
            "cours": round(prix, 2),
            "shares": float(shares_achetees),
            "investi_total": round(total_investi, 2),
            "valeur_total": round(total_shares * prix, 2)
        })

    valeur_finale = total_shares * float(df["close"].iloc[-1])
    rendement = valeur_finale - total_investi

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": round(valeur_finale, 2),
        "gain": round(rendement, 2),
        "gain_pct": round((rendement / total_investi) * 100, 2),
        "historique": historique
    }
