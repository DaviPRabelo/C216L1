from fastapi import APIRouter, Depends, Query

from app.api.dependencias import (
    obter_repositorio_de_almoxarifados,
    obter_repositorio_de_inventarios,
    obter_repositorio_de_produtos,
)
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados
from app.repositories.inventario import RepositorioDeInventarios
from app.repositories.produto import RepositorioDeProdutos
from app.schemas.inventario import (
    ContagemEntrada,
    Inventario,
    InventarioAbertura,
    InventarioResumo,
)
from app.services import almoxarifado as servico_almoxarifado
from app.services import inventario as servico

router = APIRouter(prefix="/inventarios", tags=["inventários"])

Repo = RepositorioDeInventarios


@router.get("", response_model=list[InventarioResumo])
def listar(
    almoxarifado_id: int | None = Query(default=None, description="Filtra por depósito"),
    repo: Repo = Depends(obter_repositorio_de_inventarios),
):
    return servico.listar_inventarios(repo, almoxarifado_id)


@router.get("/{inventario_id}", response_model=Inventario)
def obter(inventario_id: int, repo: Repo = Depends(obter_repositorio_de_inventarios)):
    return servico.obter_inventario(repo, inventario_id)


@router.post("", response_model=Inventario, status_code=201)
def abrir(
    entrada: InventarioAbertura,
    repo: Repo = Depends(obter_repositorio_de_inventarios),
    repo_produtos: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
    repo_almoxarifados: RepositorioDeAlmoxarifados = Depends(obter_repositorio_de_almoxarifados),
):
    servico_almoxarifado.obter_almoxarifado(repo_almoxarifados, entrada.almoxarifado_id)
    return servico.abrir_inventario(
        repo, repo_produtos, entrada.almoxarifado_id, entrada.responsavel, entrada.data
    )


@router.patch("/{inventario_id}/itens/{produto_id}", response_model=Inventario)
def contar(
    inventario_id: int,
    produto_id: int,
    entrada: ContagemEntrada,
    repo: Repo = Depends(obter_repositorio_de_inventarios),
):
    return servico.contar_item(repo, inventario_id, produto_id, entrada.quantidade_contada)


@router.post("/{inventario_id}/fechar", response_model=Inventario)
def fechar(inventario_id: int, repo: Repo = Depends(obter_repositorio_de_inventarios)):
    return servico.fechar_inventario(repo, inventario_id)
