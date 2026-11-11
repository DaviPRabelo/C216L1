from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import itens
from app.config import CORS_ORIGINS

app = FastAPI(title="API C216", version="7.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(itens.router)


@app.get("/", tags=["saude"])
def read_root():
    return {"message": "API Prática 1 C216"}
