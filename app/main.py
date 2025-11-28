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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
#  STATIC FILES (/static)
# ----------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------------------------------------
#  HOME → SERVE FRONT
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
#  AUTOCOMPLETE VIA CLOUDFLARE WORKER
# ----------------------------------------------------
WORKER_URL = "https://dca-yahoo-proxy.nico-hameau.workers.dev"

@app.get("/search")
def search_symbols(query: str):
    if len(query) < 2:
        return {"symbols": []}

    try:
        r = requests.get(
            WORKER_URL,
            params={"query": query},
            timeout=5
        )
        data = r.json()
    except Exception:
        return {"symbols": []}

    quotes = data.get("quotes", [])
    results = []

    for q in quotes[:12]:  # limite à 12 résultats
        results.append({
            "symbol": q.get("symbol"),
            "name": q.get("shortname") or q.get("longname") or "",
            "exchange": q.get("exchDisp") or "",
        })

    return {"symbols": results}
