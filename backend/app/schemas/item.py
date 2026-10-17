from pydantic import BaseModel, ConfigDict


class ItemEntrada(BaseModel):
    """Corpo de POST e PUT — todos os campos obrigatórios."""

    nome: str
    preco: float


class ItemAtualizacaoParcial(BaseModel):
    """Corpo de PATCH — todos os campos opcionais."""

    nome: str | None = None
    preco: float | None = None


class Item(ItemEntrada):
    """Resposta da API. Convertida a partir do modelo ORM."""

    model_config = ConfigDict(from_attributes=True)

    id: int
