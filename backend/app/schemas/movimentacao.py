from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TipoMovimentacao


class MovimentacaoEntrada(BaseModel):
    tipo: TipoMovimentacao
    quantidade: int
    responsavel: str
    observacao: str = ""


class Movimentacao(MovimentacaoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    criada_em: datetime