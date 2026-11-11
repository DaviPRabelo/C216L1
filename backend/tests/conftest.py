import pytest

from app.models.item import ItemORM

ITEM_PADRAO = {
    "nome": "Teclado",
    "descricao": "Mecânico",
    "categoria": "Periféricos",
    "quantidade": 2,
    "preco": 150.0,
}


class RepositorioFalso:
    """Dublê em memória do repositório, para os testes unitários."""

    def __init__(self) -> None:
        self._itens: dict[int, ItemORM] = {}
        self._proximo_id = 1

    def adicionar(
        self, nome: str, descricao: str, categoria: str, quantidade: int, preco: float
    ) -> ItemORM:
        item = ItemORM(
            id=self._proximo_id,
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            quantidade=quantidade,
            preco=preco,
        )
        self._itens[item.id] = item
        self._proximo_id += 1
        return item

    def buscar(self, item_id: int) -> ItemORM | None:
        return self._itens.get(item_id)

    def buscar_por_nome(self, nome: str) -> ItemORM | None:
        return next((item for item in self._itens.values() if item.nome == nome), None)

    def listar(self, nome_contem: str | None = None) -> list[ItemORM]:
        itens = list(self._itens.values())
        if nome_contem:
            termo = nome_contem.lower()
            itens = [item for item in itens if termo in item.nome.lower()]
        return itens

    def atualizar(
        self,
        item: ItemORM,
        nome: str,
        descricao: str,
        categoria: str,
        quantidade: int,
        preco: float,
    ) -> ItemORM:
        item.nome = nome
        item.descricao = descricao
        item.categoria = categoria
        item.quantidade = quantidade
        item.preco = preco
        return item

    def remover(self, item_id: int) -> bool:
        return self._itens.pop(item_id, None) is not None


@pytest.fixture
def repo() -> RepositorioFalso:
    """Repositório falso vazio, recriado a cada teste."""
    return RepositorioFalso()


@pytest.fixture
def repo_com_itens(repo: RepositorioFalso) -> RepositorioFalso:
    """Repositório falso já populado, para os testes de leitura."""
    repo.adicionar("Teclado", "Mecânico", "Periféricos", 2, 150.0)
    repo.adicionar("Monitor", "27 polegadas", "Eletrônicos", 1, 900.0)
    return repo
