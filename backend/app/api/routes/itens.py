from fastapi import APIRouter, Depends, HTTPException, Query

from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.repository import RepositorioDeItens
from app.schemas.item import Item, ItemAtualizacaoParcial, ItemEntrada
from app.services import item as servico

router = APIRouter(prefix="/itens", tags=["itens"])

_repositorio = RepositorioDeItens()


def obter_repositorio() -> RepositorioDeItens:
    """Dependência do repositório. Os testes a sobrescrevem para isolar o estado."""
    return _repositorio


@router.get("", response_model=list[Item])
def listar(
    nome_contem: str | None = Query(default=None, description="Filtra pelo nome"),
    repo: RepositorioDeItens = Depends(obter_repositorio),
):
    return servico.listar_itens(repo, nome_contem)


@router.get("/{item_id}", response_model=Item)
def obter(item_id: int, repo: RepositorioDeItens = Depends(obter_repositorio)):
    try:
        return servico.obter_item(repo, item_id)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro


@router.post("", response_model=Item, status_code=201)
def criar(entrada: ItemEntrada, repo: RepositorioDeItens = Depends(obter_repositorio)):
    try:
        return servico.criar_item(repo, entrada.nome, entrada.preco)
    except DadosInvalidos as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.put("/{item_id}", response_model=Item)
def substituir(
    item_id: int,
    entrada: ItemEntrada,
    repo: RepositorioDeItens = Depends(obter_repositorio),
):
    try:
        return servico.substituir_item(repo, item_id, entrada.nome, entrada.preco)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except DadosInvalidos as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.patch("/{item_id}", response_model=Item)
def atualizar(
    item_id: int,
    entrada: ItemAtualizacaoParcial,
    repo: RepositorioDeItens = Depends(obter_repositorio),
):
    try:
        return servico.atualizar_item(repo, item_id, entrada.nome, entrada.preco)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except DadosInvalidos as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.delete("/{item_id}", status_code=204)
def remover(item_id: int, repo: RepositorioDeItens = Depends(obter_repositorio)):
    try:
        servico.remover_item(repo, item_id)
    except ItemNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
