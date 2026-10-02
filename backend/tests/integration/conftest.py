import pytest
from fastapi.testclient import TestClient

from app.api.routes.itens import obter_repositorio
from app.main import app
from app.repository import RepositorioDeItens


@pytest.fixture
def client(repo: RepositorioDeItens) -> TestClient:
    """TestClient com repositório limpo, isolado por teste."""
    app.dependency_overrides[obter_repositorio] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()
