# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .dca_logic import calcul_dca

app = FastAPI()

# CORS large pour éviter les problèmes futurs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir le dossier /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servir le front sur "/"
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


@app.get("/dca")
def api_dca(symbol: str, amount: float = 100.0, start: str | None = None):
    result, error = calcul_dca(symbol=symbol, amount=amount, start=start)
    if error:
        raise HTTPException(status_code=400, detail=error["message"])
    return result
