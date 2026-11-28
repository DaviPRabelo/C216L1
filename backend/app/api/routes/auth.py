from fastapi import APIRouter, Depends

from app.api.dependencias import obter_repositorio_de_usuarios
from app.repositories.usuario import RepositorioDeUsuarios
from app.schemas.usuario import LoginEntrada, UsuarioCadastro, UsuarioPublico
from app.services import usuario as servico

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/registrar", response_model=UsuarioPublico, status_code=201)
def registrar(
    entrada: UsuarioCadastro,
    repo: RepositorioDeUsuarios = Depends(obter_repositorio_de_usuarios),
):
    return servico.registrar_usuario(
        repo,
        entrada.nome,
        entrada.email,
        entrada.senha,
        entrada.setor,
        entrada.papel,
    )


@router.post("/login", response_model=UsuarioPublico)
def login(
    entrada: LoginEntrada,
    repo: RepositorioDeUsuarios = Depends(obter_repositorio_de_usuarios),
):
    return servico.autenticar(repo, entrada.email, entrada.senha)


@router.get("/usuarios", response_model=list[UsuarioPublico])
def listar_usuarios(repo: RepositorioDeUsuarios = Depends(obter_repositorio_de_usuarios)):
    """Operadores cadastrados, para escolher o responsável por um almoxarifado."""
    return repo.listar()
