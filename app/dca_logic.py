import os
import requests
import pandas as pd
from datetime import datetime

# ⚠️ On lit la clé dans les variables d'environnement (Render)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def fetch_data(ticker: str):
    """
    Récupère l'historique mensuel du ticker via Yahoo Finance 160 (RapidAPI).
    Retourne un DataFrame indexé par date avec une colonne 'close'.
    """

    if not RAPIDAPI_KEY:
        # Erreur côté serveur : clé manquante
        return None, {"message": "RAPIDAPI_KEY manquante sur le serveur."}

    url = "https://yahoo-finance160.p.rapidapi.com/history"

    params = {
        "symbol": ticker,
        "interval": "1mo",
        "range": "max"
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        # ⚠️ Vérifie bien que c'est EXACTEMENT ce qui est indiqué dans RapidAPI > Code Snippet
        "x-rapidapi-host": "yahoo-finance160.p.rapidapi.com"
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
    except Exception as e:
        return None, {"message": f"Erreur réseau RapidAPI : {e}"}

    # Si statut HTTP pas 200 → on remonte l'erreur brute
    if r.status_code != 200:
        return None, {
            "message": f"HTTP {r.status_code} depuis RapidAPI",
            "details": r.text[:300]
        }

    try:
        data = r.json()
    except Exception as e:
        return None, {"message": f"Réponse non-JSON de RapidAPI : {e}", "raw": r.text[:300]}

    # ✅ Cas normal : la clé 'prices' est présente
    if "prices" in data:
        df = pd.DataFrame(data["prices"])
        if "date" not in df or "close" not in df:
            return None, {"message": "Format inattendu : colonnes 'date' ou 'close' manquantes.", "raw": data}

        df = df[["date", "close"]].dropna()
        df["date"] = pd.to_datetime(df["date"], unit="s")
        df = df.set_index("date").sort_index()
        return df, None

    # ❌ Cas erreur : on renvoie ce que l’API a répondu
    return None, {
        "message": "Pas de clé 'prices' dans la réponse RapidAPI.",
        "raw": data
    }


def calcul_dca(ticker: str, montant: float, start: str):
    """
    Calcule un DCA mensuel à partir des données RapidAPI.
    - ticker : symbole boursier (AAPL, MSFT, etc.)
    - montant : montant investi chaque mois
    - start : date de départ, ex '2010-01-01'
    """

    df, err = fetch_data(ticker)

    if err is not None:
        # On renvoie l’erreur telle quelle à FastAPI
        return {"error": err["message"], "details": err.get("raw")}

    # Filtrage sur la date de départ
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return {"error": f"Format de date invalide pour start : {start}. Utilise AAAA-MM-JJ."}

    df = df[df.index >= start_dt]

    if df.empty:
        return {"error": f"Aucune donnée trouvée pour {ticker} à partir de {start}."}

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
        return {"error": f"Aucune donnée exploitable (prix <= 0) pour {ticker}."}

    valeur_finale = historique[-1]["valeur_total"]
    gain = round(valeur_finale - total_investi, 2)

    return {
        "ticker": ticker,
        "investi_total": round(total_investi, 2),
        "valeur_finale": valeur_finale,
        "gain": gain,
        "gain_pct": round((gain / total_investi) * 100, 2) if total_investi > 0 else 0,
        "historique": historique
    }
