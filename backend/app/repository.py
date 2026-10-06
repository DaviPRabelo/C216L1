from app.schemas.item import Item


class RepositorioDeItens:
    """Armazenamento em memória. Na Prática 4 vira PostgreSQL."""

    def __init__(self) -> None:
        self._itens: dict[int, Item] = {}
        self._proximo_id = 1

    def adicionar(self, nome: str, preco: float) -> Item:
        item = Item(id=self._proximo_id, nome=nome, preco=preco)
        self._itens[item.id] = item
        self._proximo_id += 1
        return item

    def buscar(self, item_id: int) -> Item | None:
        return self._itens.get(item_id)

    def listar(self) -> list[Item]:
        return list(self._itens.values())

    def remover(self, item_id: int) -> bool:
        return self._itens.pop(item_id, None) is not None

    def salvar(self, item: Item) -> Item:
        """Grava um item já existente, preservando o id."""
        self._itens[item.id] = item
        return item

