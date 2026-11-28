from app.errors import CredenciaisInvalidas, DadosInvalidos, EmailJaExiste
from app.models.enums import PapelUsuario
from app.models.usuario import UsuarioORM
from app.repositories.usuario import RepositorioDeUsuarios
from app.security import SENHA_MAXIMA, conferir_senha, gerar_hash

SENHA_MINIMA = 6


def _validar(nome: str, email: str, setor: str, senha: str) -> tuple[str, str, str]:
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    setor = (setor or "").strip()
    senha = senha or ""

    if not nome:
        raise DadosInvalidos("O nome é obrigatório")
    if len(nome) > 100:
        raise DadosInvalidos("O nome deve ter até 100 caracteres")
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise DadosInvalidos("Informe um e-mail válido")
    if len(email) > 120:
        raise DadosInvalidos("O e-mail deve ter até 120 caracteres")
    if len(setor) > 50:
        raise DadosInvalidos("O setor deve ter até 50 caracteres")
    if len(senha) < SENHA_MINIMA:
        raise DadosInvalidos(f"A senha deve ter pelo menos {SENHA_MINIMA} caracteres")
    if len(senha.encode()) > SENHA_MAXIMA:
        raise DadosInvalidos("A senha é longa demais")

    return nome, email, setor


def registrar_usuario(
    repo: RepositorioDeUsuarios,
    nome: str,
    email: str,
    senha: str,
    setor: str = "",
    papel: PapelUsuario = PapelUsuario.EMPREGADO,
) -> UsuarioORM:
    nome, email, setor = _validar(nome, email, setor, senha)

    if repo.buscar_por_email(email) is not None:
        raise EmailJaExiste(email)

    try:
        papel = PapelUsuario(papel)
    except ValueError as erro:
        raise DadosInvalidos("Papel de usuário inválido") from erro

    return repo.adicionar(nome, email, setor, gerar_hash(senha), papel)


def autenticar(repo: RepositorioDeUsuarios, email: str, senha: str) -> UsuarioORM:
    usuario = repo.buscar_por_email((email or "").strip().lower())
    if usuario is None or not conferir_senha(senha or "", usuario.senha_hash):
        raise CredenciaisInvalidas()
    return usuario
