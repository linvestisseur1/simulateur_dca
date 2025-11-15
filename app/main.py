from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.dca_logic import calcul_dca
import os

app = FastAPI(title="Simulateur DCA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_front():
    return FileResponse("static/index.html")


@app.get("/dca")
def api_dca(ticker: str, montant: float = 100, start: str = "2000-01-01"):

    api_key = os.getenv("RAPIDAPI_KEY")

    result = calcul_dca(ticker, montant, start, api_key)

    return result
