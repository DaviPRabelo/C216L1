from pydantic import BaseModel, ConfigDict


class UsuarioCadastro(BaseModel):
    nome: str
    email: str
    setor: str = ""
    senha: str


class LoginEntrada(BaseModel):
    email: str
    senha: str


class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    setor: str