from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dca_logic import calcul_dca

app = FastAPI(
    title="Simulateur DCA API",
    description="API simple et rapide pour simuler du Dollar-Cost Averaging.",
    version="1.0.0"
)

# CORS (permettra un frontend plus tard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.get("/")
def home():
    return {"status": "ok", "message": "Simulateur DCA prêt"}

@app.get("/dca")
def api_dca(ticker: str, montant: float = 100, start: str = "2000-01-01"):
    return calcul_dca(ticker, montant, start)
