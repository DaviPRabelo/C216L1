from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos


def obter_repositorio_de_produtos(
    sessao: Session = Depends(get_session),
) -> RepositorioDeProdutos:
    return RepositorioDeProdutos(sessao)


def obter_repositorio_de_movimentacoes(
    sessao: Session = Depends(get_session),
) -> RepositorioDeMovimentacoes:
    return RepositorioDeMovimentacoes(sessao)
