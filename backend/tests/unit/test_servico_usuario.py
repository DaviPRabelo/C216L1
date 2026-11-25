import pytest

from app.errors import CredenciaisInvalidas, DadosInvalidos, EmailJaExiste
from app.services import usuario as servico
from tests.conftest import USUARIO_PADRAO


def test_registrar_usuario(repo_usuarios):
    usuario = servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    assert usuario.id == 1
    assert usuario.nome == "Davi"
    assert usuario.setor == "TI"


def test_senha_nunca_e_guardada_em_texto(repo_usuarios):
    usuario = servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    assert usuario.senha_hash != "senha123"
    assert "senha123" not in usuario.senha_hash
    assert usuario.senha_hash.startswith("$2b$")


def test_email_e_normalizado_para_minusculo(repo_usuarios):
    usuario = servico.registrar_usuario(
        repo_usuarios, **{**USUARIO_PADRAO, "email": "  DAVI@ALMOX.COM  "}
    )

    assert usuario.email == "davi@almox.com"


def test_nome_e_setor_perdem_espacos(repo_usuarios):
    usuario = servico.registrar_usuario(
        repo_usuarios, **{**USUARIO_PADRAO, "nome": "  Davi  ", "setor": "  TI  "}
    )

    assert (usuario.nome, usuario.setor) == ("Davi", "TI")


def test_email_duplicado_e_recusado(repo_usuarios):
    servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    with pytest.raises(EmailJaExiste):
        servico.registrar_usuario(repo_usuarios, **{**USUARIO_PADRAO, "nome": "Outro"})


def test_email_duplicado_ignora_maiusculas(repo_usuarios):
    servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    with pytest.raises(EmailJaExiste):
        servico.registrar_usuario(repo_usuarios, **{**USUARIO_PADRAO, "email": "DAVI@ALMOX.COM"})


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("nome", "   "),
        ("nome", "N" * 101),
        ("email", ""),
        ("email", "semarroba.com"),
        ("email", "sem@dominio"),
        ("setor", "S" * 51),
        ("senha", ""),
        ("senha", "12345"),
        ("senha", "x" * 73),
    ],
)
def test_cadastro_invalido(repo_usuarios, campo, valor):
    with pytest.raises(DadosInvalidos):
        servico.registrar_usuario(repo_usuarios, **{**USUARIO_PADRAO, campo: valor})


def test_autenticar_com_credenciais_corretas(repo_usuarios):
    cadastrado = servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    autenticado = servico.autenticar(repo_usuarios, "davi@almox.com", "senha123")

    assert autenticado.id == cadastrado.id


def test_autenticar_aceita_email_em_maiusculo(repo_usuarios):
    servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    assert servico.autenticar(repo_usuarios, "DAVI@ALMOX.COM", "senha123") is not None


def test_autenticar_com_senha_errada(repo_usuarios):
    servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    with pytest.raises(CredenciaisInvalidas):
        servico.autenticar(repo_usuarios, "davi@almox.com", "errada")


def test_autenticar_com_email_inexistente(repo_usuarios):
    with pytest.raises(CredenciaisInvalidas):
        servico.autenticar(repo_usuarios, "ninguem@almox.com", "senha123")


def test_mensagem_nao_revela_se_o_email_existe(repo_usuarios):
    servico.registrar_usuario(repo_usuarios, **USUARIO_PADRAO)

    with pytest.raises(CredenciaisInvalidas) as senha_errada:
        servico.autenticar(repo_usuarios, "davi@almox.com", "errada")
    with pytest.raises(CredenciaisInvalidas) as email_inexistente:
        servico.autenticar(repo_usuarios, "ninguem@almox.com", "senha123")

    assert str(senha_errada.value) == str(email_inexistente.value)