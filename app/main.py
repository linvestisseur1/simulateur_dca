# app/main.py
import os
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .dca_logic import calcul_dca

app = FastAPI()

# ----------------------------------------------------
#  CORS
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu pourras restreindre plus tard
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
#  SERVE STATIC FILES  (/static/…)
# ----------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------------------------------------
#  SERVE FRONT PAGE  (/)
# ----------------------------------------------------
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# ----------------------------------------------------
#  DCA ENDPOINT  (/dca)
# ----------------------------------------------------
@app.get("/dca")
def api_dca(symbol: str, amount: float = 100.0, start: str | None = None):
    """
    Exemple :
    /dca?symbol=AAPL&amount=100&start=2000-01-01
    """
    result, error = calcul_dca(symbol=symbol, amount=amount, start=start)
    if error:
        raise HTTPException(status_code=400, detail=error["message"])
    return result

# ----------------------------------------------------
#  AUTO-COMPLÉTION  (/search)
# ----------------------------------------------------
TWELVEDATA_KEY = os.getenv("TWELVEDATA_KEY")

@app.get("/search")
def search_symbol(query: str):
    """
    Auto-complétion dynamique pour les symboles financiers.
    Utilise l'API TwelveData : symbol_search
    """
    if not TWELVEDATA_KEY:
        raise HTTPException(status_code=500, detail="TWELVEDATA_KEY manquante sur le serveur.")

    if len(query) < 2:
        return {"symbols": []}

    url = "https://api.twelvedata.com/symbol_search"
    params = {"symbol": query, "apikey": TWELVEDATA_KEY}

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
    except Exception:
        return {"symbols": []}

    results = data.get("data", [])

    # On nettoie et on limite le nombre de suggestions
    clean_list = []
    for item in results[:12]:
        clean_list.append({
            "symbol": item.get("symbol"),
            "name": item.get("instrument_name") or item.get("name") or "",
            "exchange": item.get("exchange") or "",
        })

    return {"symbols": clean_list}
