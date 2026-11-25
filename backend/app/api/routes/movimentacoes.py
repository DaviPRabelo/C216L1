from fastapi import APIRouter, Depends

from app.api.dependencias import (
    obter_repositorio_de_movimentacoes,
    obter_repositorio_de_produtos,
)
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos
from app.schemas.movimentacao import Movimentacao, MovimentacaoEntrada
from app.services import movimentacao as servico

router = APIRouter(prefix="/produtos/{produto_id}/movimentacoes", tags=["movimentações"])


@router.get("", response_model=list[Movimentacao])
def listar(
    produto_id: int,
    repo_produtos: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
    repo_movimentacoes: RepositorioDeMovimentacoes = Depends(obter_repositorio_de_movimentacoes),
):
    return servico.listar_movimentacoes(repo_produtos, repo_movimentacoes, produto_id)


@router.post("", response_model=Movimentacao, status_code=201)
def registrar(
    produto_id: int,
    entrada: MovimentacaoEntrada,
    repo_produtos: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
    repo_movimentacoes: RepositorioDeMovimentacoes = Depends(obter_repositorio_de_movimentacoes),
):
    return servico.registrar_movimentacao(
        repo_produtos,
        repo_movimentacoes,
        produto_id,
        tipo=entrada.tipo,
        quantidade=entrada.quantidade,
        responsavel=entrada.responsavel,
        observacao=entrada.observacao,
    )
