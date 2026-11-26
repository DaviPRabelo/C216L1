import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import (
    obter_repositorio_de_almoxarifados,
    obter_repositorio_de_movimentacoes,
    obter_repositorio_de_produtos,
    obter_repositorio_de_usuarios,
)
from app.database.base import Base
from app.main import app
from app.models import (  # noqa: F401 — registra as tabelas
    AlmoxarifadoORM,
    MovimentacaoORM,
    ProdutoORM,
)
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos
from app.repositories.usuario import RepositorioDeUsuarios

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://admin:adminpassword@localhost:5432/almoxarifado_test",
)


def _garantir_banco_de_teste(url: str) -> None:
    base, nome = url.rsplit("/", 1)
    admin = create_engine(f"{base}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conexao:
        existe = conexao.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"), {"nome": nome}
        ).scalar()
        if not existe:
            conexao.execute(text(f'CREATE DATABASE "{nome}"'))
    admin.dispose()


@pytest.fixture
def repo_usuarios(sessao) -> RepositorioDeUsuarios:
    return RepositorioDeUsuarios(sessao)


@pytest.fixture(scope="session")
def engine_de_teste():
    _garantir_banco_de_teste(TEST_DATABASE_URL)
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sessao(engine_de_teste):
    """Sessão real, com as tabelas limpas ao final de cada teste."""
    Sessao = sessionmaker(bind=engine_de_teste, expire_on_commit=False)
    with Sessao() as sessao:
        yield sessao
    with engine_de_teste.begin() as conexao:
        nomes = ", ".join(t.name for t in Base.metadata.sorted_tables)
        conexao.execute(text(f"TRUNCATE {nomes} RESTART IDENTITY CASCADE"))


@pytest.fixture
def repo(sessao) -> RepositorioDeProdutos:
    return RepositorioDeProdutos(sessao)


@pytest.fixture
def repo_movimentacoes(sessao) -> RepositorioDeMovimentacoes:
    return RepositorioDeMovimentacoes(sessao)


@pytest.fixture
def client(repo, repo_movimentacoes, repo_usuarios, repo_almoxarifados) -> TestClient:
    """TestClient com os três repositórios sobre a mesma sessão de teste."""
    app.dependency_overrides[obter_repositorio_de_produtos] = lambda: repo
    app.dependency_overrides[obter_repositorio_de_movimentacoes] = lambda: repo_movimentacoes
    app.dependency_overrides[obter_repositorio_de_usuarios] = lambda: repo_usuarios
    app.dependency_overrides[obter_repositorio_de_almoxarifados] = lambda: repo_almoxarifados
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def repo_almoxarifados(sessao) -> RepositorioDeAlmoxarifados:
    return RepositorioDeAlmoxarifados(sessao)


@pytest.fixture(autouse=True)
def deposito(request, sessao):
    """Almoxarifado padrao criado antes de cada teste de rota, sempre com id 1."""
    if "engine_de_teste" not in request.fixturenames:
        return None
    return RepositorioDeAlmoxarifados(sessao).adicionar(
        nome="Central", local="Galpao A", responsavel="Davi", ativo=True
    )
