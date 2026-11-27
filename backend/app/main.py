from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import almoxarifados, auth, inventarios, movimentacoes, produtos
from app.api.tratamento_de_erros import registrar_tratadores
from app.config import CORS_ORIGINS

app = FastAPI(
    title="Almoxarifado C216",
    description="Controle de estoque com produtos e movimentações de entrada e saída.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(auth.router)
app.include_router(almoxarifados.router)
registrar_tratadores(app)

app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(inventarios.router)


@app.get("/", tags=["saude"])
def saude():
    return {"status": "ok", "servico": "almoxarifado"}
