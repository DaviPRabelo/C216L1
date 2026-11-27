from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados
from app.repositories.inventario import RepositorioDeInventarios
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos
from app.repositories.usuario import RepositorioDeUsuarios


def obter_repositorio_de_produtos(
    sessao: Session = Depends(get_session),
) -> RepositorioDeProdutos:
    return RepositorioDeProdutos(sessao)


def obter_repositorio_de_movimentacoes(
    sessao: Session = Depends(get_session),
) -> RepositorioDeMovimentacoes:
    return RepositorioDeMovimentacoes(sessao)


def obter_repositorio_de_usuarios(
    sessao: Session = Depends(get_session),
) -> RepositorioDeUsuarios:
    return RepositorioDeUsuarios(sessao)


def obter_repositorio_de_almoxarifados(
    sessao: Session = Depends(get_session),
) -> RepositorioDeAlmoxarifados:
    return RepositorioDeAlmoxarifados(sessao)


def obter_repositorio_de_inventarios(
    sessao: Session = Depends(get_session),
) -> RepositorioDeInventarios:
    return RepositorioDeInventarios(sessao)
