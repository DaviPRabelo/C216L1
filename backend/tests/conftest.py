import pytest

from app.repository import RepositorioDeItens


@pytest.fixture
def repo() -> RepositorioDeItens:
    """Repositório vazio, recriado a cada teste."""
    return RepositorioDeItens()


@pytest.fixture
def repo_com_itens(repo: RepositorioDeItens) -> RepositorioDeItens:
    """Repositório já populado, para os testes de leitura."""
    repo.adicionar("Teclado", 150.0)
    repo.adicionar("Monitor", 900.0)
    return repo
