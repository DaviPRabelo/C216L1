from fastapi import FastAPI

from app.api.routes import itens

app = FastAPI(title="API C216", version="4.0.0")

app.include_router(itens.router)


@app.get("/", tags=["saude"])
def read_root():
    return {"message": "API Prática 1 C216"}