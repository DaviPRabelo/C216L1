from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusInventario


class InventarioAbertura(BaseModel):
    almoxarifado_id: int
    responsavel: str
    data: date | None = None


class ContagemEntrada(BaseModel):
    quantidade_contada: int


class ContagemItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    produto_codigo: str
    produto_nome: str
    unidade: str
    saldo_sistema: int
    quantidade_contada: int | None
    divergencia: int | None


class InventarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    almoxarifado_id: int
    data: date
    responsavel: str
    status: StatusInventario
    criado_em: datetime
    itens_contados: int
    itens_divergentes: int


class Inventario(InventarioResumo):
    itens: list[ContagemItem]
