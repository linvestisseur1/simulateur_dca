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
#  AUTO-COMPLÉTION  (/search) — VERSION YAHOO FINANCE
# ----------------------------------------------------
@app.get("/search")
def search_yahoo(query: str):
    """
    Auto-complétion basée sur Yahoo Finance.
    Compatible à 100% avec yfinance.
    """
    if len(query) < 2:
        return {"symbols": []}

    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query}

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
    except Exception:
        return {"symbols": []}

    results = data.get("quotes", [])
    clean_list = []

    for item in results[:12]:
        symbol = item.get("symbol")
        name = item.get("shortname") or ""
        exchange = item.get("exchDisp") or ""

        if not symbol:
            continue

        clean_list.append({
            "symbol": symbol,
            "name": name,
            "exchange": exchange
        })

    return {"symbols": clean_list}
