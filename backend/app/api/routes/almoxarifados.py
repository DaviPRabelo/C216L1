from fastapi import APIRouter, Depends, Query

from app.api.dependencias import obter_repositorio_de_almoxarifados
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados
from app.schemas.almoxarifado import (
    Almoxarifado,
    AlmoxarifadoAtualizacao,
    AlmoxarifadoEntrada,
    AlmoxarifadoResumo,
)
from app.services import almoxarifado as servico

router = APIRouter(prefix="/almoxarifados", tags=["almoxarifados"])

Repo = RepositorioDeAlmoxarifados


@router.get("", response_model=list[AlmoxarifadoResumo])
def listar(
    apenas_ativos: bool = Query(default=False, description="Esconde os desativados"),
    repo: Repo = Depends(obter_repositorio_de_almoxarifados),
):
    return servico.resumir_almoxarifados(repo, apenas_ativos)


@router.get("/{almoxarifado_id}", response_model=Almoxarifado)
def obter(almoxarifado_id: int, repo: Repo = Depends(obter_repositorio_de_almoxarifados)):
    return servico.obter_almoxarifado(repo, almoxarifado_id)


@router.post("", response_model=Almoxarifado, status_code=201)
def criar(entrada: AlmoxarifadoEntrada, repo: Repo = Depends(obter_repositorio_de_almoxarifados)):
    return servico.criar_almoxarifado(
        repo, entrada.nome, entrada.local, entrada.responsavel, entrada.ativo
    )


@router.put("/{almoxarifado_id}", response_model=Almoxarifado)
def substituir(
    almoxarifado_id: int,
    entrada: AlmoxarifadoEntrada,
    repo: Repo = Depends(obter_repositorio_de_almoxarifados),
):
    return servico.atualizar_almoxarifado(
        repo,
        almoxarifado_id,
        nome=entrada.nome,
        local=entrada.local,
        responsavel=entrada.responsavel,
        ativo=entrada.ativo,
    )


@router.patch("/{almoxarifado_id}", response_model=Almoxarifado)
def atualizar(
    almoxarifado_id: int,
    entrada: AlmoxarifadoAtualizacao,
    repo: Repo = Depends(obter_repositorio_de_almoxarifados),
):
    return servico.atualizar_almoxarifado(
        repo, almoxarifado_id, **entrada.model_dump(exclude_unset=True)
    )


@router.delete("/{almoxarifado_id}", status_code=204)
def remover(almoxarifado_id: int, repo: Repo = Depends(obter_repositorio_de_almoxarifados)):
    servico.remover_almoxarifado(repo, almoxarifado_id)
