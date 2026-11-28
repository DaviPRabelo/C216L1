import pytest

from app.errors import (
    AlmoxarifadoComProdutos,
    AlmoxarifadoNaoEncontrado,
    DadosInvalidos,
    NomeDeAlmoxarifadoJaExiste,
)
from app.models.enums import PapelUsuario
from app.services import almoxarifado as servico
from tests.conftest import ALMOXARIFADO_PADRAO


def test_criar_almoxarifado(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    assert criado.id == 1
    assert criado.nome == "Central"
    assert criado.ativo is True


def test_campos_perdem_espacos(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, nome="  Obras  ", local="  Patio  ")

    assert (criado.nome, criado.local) == ("Obras", "Patio")


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("nome", "   "),
        ("nome", "N" * 81),
        ("local", "L" * 121),
    ],
)
def test_criar_invalido(repo_almoxarifados, campo, valor):
    with pytest.raises(DadosInvalidos):
        servico.criar_almoxarifado(repo_almoxarifados, **{**ALMOXARIFADO_PADRAO, campo: valor})


def test_nome_duplicado_e_recusado(repo_almoxarifados):
    servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    with pytest.raises(NomeDeAlmoxarifadoJaExiste):
        servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)


def test_nome_duplicado_ignora_maiusculas(repo_almoxarifados):
    servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    with pytest.raises(NomeDeAlmoxarifadoJaExiste):
        servico.criar_almoxarifado(repo_almoxarifados, nome="CENTRAL")


def test_obter_inexistente(repo_almoxarifados):
    with pytest.raises(AlmoxarifadoNaoEncontrado):
        servico.obter_almoxarifado(repo_almoxarifados, 999)


def test_listar_apenas_ativos(repo_almoxarifados):
    servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)
    servico.criar_almoxarifado(repo_almoxarifados, nome="Desativado", ativo=False)

    assert [a.nome for a in servico.listar_almoxarifados(repo_almoxarifados)] == [
        "Central",
        "Desativado",
    ]
    assert [a.nome for a in servico.listar_almoxarifados(repo_almoxarifados, True)] == ["Central"]


def test_atualizar_preserva_campos_nao_enviados(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    atualizado = servico.atualizar_almoxarifado(repo_almoxarifados, criado.id, local="Galpao B")

    assert atualizado.local == "Galpao B"
    assert atualizado.nome == "Central"


def test_atualizar_mantendo_o_proprio_nome(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    atualizado = servico.atualizar_almoxarifado(repo_almoxarifados, criado.id, nome="Central")

    assert atualizado.nome == "Central"


def test_atualizar_com_nome_de_outro(repo_almoxarifados):
    primeiro = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)
    servico.criar_almoxarifado(repo_almoxarifados, nome="Obras")

    with pytest.raises(NomeDeAlmoxarifadoJaExiste):
        servico.atualizar_almoxarifado(repo_almoxarifados, primeiro.id, nome="Obras")


def test_desativar_sem_excluir(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    atualizado = servico.atualizar_almoxarifado(repo_almoxarifados, criado.id, ativo=False)

    assert atualizado.ativo is False


def test_remover_sem_produtos(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)

    servico.remover_almoxarifado(repo_almoxarifados, criado.id)

    assert repo_almoxarifados.buscar(criado.id) is None


def test_remover_com_produtos_e_recusado(repo_almoxarifados):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)
    repo_almoxarifados._produtos_por_almoxarifado[criado.id] = 3

    with pytest.raises(AlmoxarifadoComProdutos):
        servico.remover_almoxarifado(repo_almoxarifados, criado.id)


def test_responsavel_empregado_e_aceito(repo_almoxarifados, repo_usuarios):
    empregado = repo_usuarios.adicionar("Davi", "davi@almox.com", "TI", "hash")

    criado = servico.criar_almoxarifado(
        repo_almoxarifados,
        nome="Obras",
        responsavel_id=empregado.id,
        repo_usuarios=repo_usuarios,
    )

    assert criado.responsavel_id == empregado.id


@pytest.mark.parametrize("papel", [PapelUsuario.ADMIN, PapelUsuario.GERENTE])
def test_responsavel_precisa_ser_empregado(repo_almoxarifados, repo_usuarios, papel):
    """Admin e gerente administram o sistema; o estoque fica com o empregado."""
    chefia = repo_usuarios.adicionar("Ana", "ana@almox.com", "Compras", "hash", papel)

    with pytest.raises(DadosInvalidos):
        servico.criar_almoxarifado(
            repo_almoxarifados,
            nome="Obras",
            responsavel_id=chefia.id,
            repo_usuarios=repo_usuarios,
        )


def test_responsavel_inexistente_e_recusado(repo_almoxarifados, repo_usuarios):
    with pytest.raises(DadosInvalidos):
        servico.criar_almoxarifado(
            repo_almoxarifados, nome="Obras", responsavel_id=999, repo_usuarios=repo_usuarios
        )


def test_atualizar_troca_o_responsavel(repo_almoxarifados, repo_usuarios):
    criado = servico.criar_almoxarifado(repo_almoxarifados, **ALMOXARIFADO_PADRAO)
    empregado = repo_usuarios.adicionar("Davi", "davi@almox.com", "TI", "hash")

    atualizado = servico.atualizar_almoxarifado(
        repo_almoxarifados,
        criado.id,
        responsavel_id=empregado.id,
        repo_usuarios=repo_usuarios,
    )

    assert atualizado.responsavel_id == empregado.id
