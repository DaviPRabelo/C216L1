import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import (
    obter_repositorio_de_movimentacoes,
    obter_repositorio_de_produtos,
)
from app.database.base import Base
from app.main import app
from app.models import MovimentacaoORM, ProdutoORM  # noqa: F401 — registra as tabelas
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos

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
        for tabela in reversed(Base.metadata.sorted_tables):
            conexao.execute(tabela.delete())


@pytest.fixture
def repo(sessao) -> RepositorioDeProdutos:
    return RepositorioDeProdutos(sessao)


@pytest.fixture
def repo_movimentacoes(sessao) -> RepositorioDeMovimentacoes:
    return RepositorioDeMovimentacoes(sessao)


@pytest.fixture
def client(repo, repo_movimentacoes) -> TestClient:
    """TestClient com os dois repositórios sobre a mesma sessão de teste."""
    app.dependency_overrides[obter_repositorio_de_produtos] = lambda: repo
    app.dependency_overrides[obter_repositorio_de_movimentacoes] = lambda: repo_movimentacoes
    yield TestClient(app)
    app.dependency_overrides.clear()