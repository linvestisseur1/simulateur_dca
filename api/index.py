from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HOME ---
@app.get("/")
def home():
    return {"status": "ok", "message": "API DCA opérationnelle 🚀"}

# --- DCA ---
@app.get("/dca")
def api_dca(ticker: str, montant: float = 100, start: str = "2000-01-01"):
    try:
        data = yf.download(ticker, start=start)

        if data.empty:
            return {"error": "Ticker introuvable"}

        close = data["Close"]
        if close.empty:
            return {"error": "Données de prix indisponibles"}

        shares = 0
        total_investi = 0

        monthly = close.resample("M").first()

        for price in monthly:
            if pd.isna(price):
                continue
            total_investi += montant
            shares += montant / price

        valeur_finale = shares * close.iloc[-1]

        return {
            "ticker": ticker,
            "total_investi": round(total_investi, 2),
            "portefeuille": round(valeur_finale, 2),
            "profit": round(valeur_finale - total_investi, 2)
        }

    except Exception as e:
        return {"error": str(e)}
