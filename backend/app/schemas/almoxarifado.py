from pydantic import BaseModel, ConfigDict


class AlmoxarifadoEntrada(BaseModel):
    nome: str
    local: str = ""
    responsavel: str = ""
    ativo: bool = True


class AlmoxarifadoAtualizacao(BaseModel):
    nome: str | None = None
    local: str | None = None
    responsavel: str | None = None
    ativo: bool | None = None


class Almoxarifado(AlmoxarifadoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AlmoxarifadoResumo(Almoxarifado):
    """Almoxarifado com os números do estoque, para a tela de seleção."""

    total_produtos: int
    produtos_em_falta: int
    unidades_em_estoque: int
