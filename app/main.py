from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.dca_logic import calcul_dca

app = FastAPI(
    title="Simulateur DCA API",
    description="API simple et rapide pour simuler du Dollar-Cost Averaging.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "message": "Simulateur DCA prêt"}

@app.get("/dca")
def api_dca(ticker: str, montant: float = 100, start: str = "2000-01-01"):
    result = calcul_dca(ticker, montant, start)

    if "error" in result:
        # On remonte l’erreur côté client (ton front affichera le message)
        raise HTTPException(status_code=400, detail=result)

    return result
