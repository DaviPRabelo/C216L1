from pydantic import BaseModel


class ItemEntrada(BaseModel):
    nome: str
    preco: float


class Item(ItemEntrada):
    id: int
