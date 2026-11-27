from pydantic import BaseModel, ConfigDict

from app.models.enums import UnidadeMedida


class ProdutoEntrada(BaseModel):
    almoxarifado_id: int
    codigo: str
    nome: str
    descricao: str = ""
    categoria: str
    unidade: UnidadeMedida
    estoque_minimo: int = 0
    foto: str = ""


class ProdutoAtualizacao(BaseModel):
    almoxarifado_id: int | None = None
    codigo: str | None = None
    nome: str | None = None
    descricao: str | None = None
    categoria: str | None = None
    unidade: UnidadeMedida | None = None
    estoque_minimo: int | None = None
    foto: str | None = None


class Produto(ProdutoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int
    saldo: int
    abaixo_do_minimo: bool
