from fastapi import FastAPI, HTTPException

from app import services
from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.models import Item, ItemEntrada
from app.repository import RepositorioDeItens

app = FastAPI(title="API C216")
repositorio = RepositorioDeItens()


@app.get("/")
def read_root():
    return {"message": "API Prática 1 C216"}


@app.get("/itens", response_model=list[Item])
def listar_itens():
    return repositorio.listar()


@app.post("/itens", response_model=Item, status_code=201)
def criar(entrada: ItemEntrada):
    try:
        return services.criar_item(repositorio, entrada.nome, entrada.preco)
    except DadosInvalidos as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@app.get("/itens/{item_id}", response_model=Item)
def obter(item_id: int):
    try:
        return services.obter_item(repositorio, item_id)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro


@app.delete("/itens/{item_id}", status_code=204)
def remover(item_id: int):
    try:
        services.remover_item(repositorio, item_id)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
