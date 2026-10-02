from pydantic import BaseModel


class ItemEntrada(BaseModel):
    """Corpo de POST e PUT — todos os campos obrigatórios."""

    nome: str
    preco: float


class ItemAtualizacaoParcial(BaseModel):
    """Corpo de PATCH — todos os campos opcionais."""

    nome: str | None = None
    preco: float | None = None


class Item(ItemEntrada):
    """Representação completa, com o identificador."""

    id: int
