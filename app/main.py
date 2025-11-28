# app/main.py
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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
#  STATIC FILES
# ----------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------------------------------------
#  HOME
# ----------------------------------------------------
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# ----------------------------------------------------
#  DCA ENDPOINT
# ----------------------------------------------------
@app.get("/dca")
def api_dca(symbol: str, amount: float = 100.0, start: str | None = None):
    result, error = calcul_dca(symbol=symbol, amount=amount, start=start)
    if error:
        raise HTTPException(status_code=400, detail=error["message"])
    return result

# ----------------------------------------------------
#  AUTO-COMPLÉTION – VERSION YAHOO (remplace TwelveData)
# ----------------------------------------------------
@app.get("/search")
def search_yahoo(query: str):
    """
    Auto-complétion compatible yfinance via Yahoo Search API.
    """
    if len(query) < 2:
        return {"symbols": []}

    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query}

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
    except:
        return {"symbols": []}

    results = data.get("quotes", [])
    clean_list = []

    for item in results[:12]:
        symbol = item.get("symbol")
        name = item.get("shortname") or item.get("longname") or ""
        exchange = item.get("exchDisp") or ""

        if symbol:
            clean_list.append({
                "symbol": symbol,
                "name": name,
                "exchange": exchange
            })

    return {"symbols": clean_list}
