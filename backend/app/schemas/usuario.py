from pydantic import BaseModel, ConfigDict

from app.models.enums import PapelUsuario


class UsuarioCadastro(BaseModel):
    nome: str
    email: str
    setor: str = ""
    senha: str
    papel: PapelUsuario = PapelUsuario.EMPREGADO


class LoginEntrada(BaseModel):
    email: str
    senha: str


class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    setor: str
    papel: PapelUsuario
