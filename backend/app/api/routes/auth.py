from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.repositories.usuario import RepositorioDeUsuarios
from app.schemas.usuario import LoginEntrada, UsuarioCadastro, UsuarioPublico
from app.services import usuario as servico

router = APIRouter(prefix="/auth", tags=["autenticação"])


def obter_repositorio(sessao: Session = Depends(get_session)) -> RepositorioDeUsuarios:
    return RepositorioDeUsuarios(sessao)


@router.post("/registrar", response_model=UsuarioPublico, status_code=201)
def registrar(
    entrada: UsuarioCadastro,
    repo: RepositorioDeUsuarios = Depends(obter_repositorio),
):
    return servico.registrar_usuario(
        repo, entrada.nome, entrada.email, entrada.senha, entrada.setor
    )


@router.post("/login", response_model=UsuarioPublico)
def login(
    entrada: LoginEntrada,
    repo: RepositorioDeUsuarios = Depends(obter_repositorio),
):
    return servico.autenticar(repo, entrada.email, entrada.senha)
