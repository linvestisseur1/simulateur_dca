# app/main.py
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .dca_logic import calcul_dca

app = FastAPI(
    title="DCA Simulator API",
    version="1.0.0",
)

# CORS large pour test / front hébergé ailleurs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tu pourras restreindre quand tout sera en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/dca")
def api_dca(
    symbol: str,
    amount: float = 100.0,
    start: Optional[str] = None,
):
    """
    Exemple : /dca?symbol=AAPL&amount=100&start=2000-01-01
    """
    result, error = calcul_dca(symbol=symbol, amount=amount, start=start)
    if error:
        raise HTTPException(status_code=400, detail=error["message"])
    return result
