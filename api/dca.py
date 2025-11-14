from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dca_logic import calcul_dca

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "message": "API DCA opérationnelle 🔥"}

@app.get("/dca")
def api_dca(ticker: str, montant: float = 100, start: str = "2000-01-01"):
    return calcul_dca(ticker, montant, start)
