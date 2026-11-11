class ErroDeDominio(Exception):
    """Erro base da aplicação."""


class ItemNaoEncontrado(ErroDeDominio):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Item {item_id} não encontrado")


class DadosInvalidos(ErroDeDominio):
    pass


class NomeJaExiste(ErroDeDominio):
    def __init__(self, nome: str):
        self.nome = nome
        super().__init__("Já existe um item com esse nome")
