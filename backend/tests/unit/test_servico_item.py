import pytest

from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.services import item as services


def test_criar_item_valido(repo):
    item = services.criar_item(repo, "Teclado", 150.0)

    assert item.id == 1
    assert item.nome == "Teclado"
    assert item.preco == 150.0


def test_criar_item_remove_espacos_do_nome(repo):
    item = services.criar_item(repo, "  Mouse  ", 80.0)

    assert item.nome == "Mouse"


def test_ids_sao_sequenciais(repo):
    primeiro = services.criar_item(repo, "Teclado", 150.0)
    segundo = services.criar_item(repo, "Mouse", 80.0)

    assert primeiro.id == 1
    assert segundo.id == 2


@pytest.mark.parametrize(
    "nome, preco",
    [
        ("", 10.0),
        ("   ", 10.0),
        ("Teclado", -1.0),
        ("Teclado", -0.01),
        ("Teclado", 1_000_001),
    ],
)
def test_criar_item_invalido_levanta_erro(repo, nome, preco):
    with pytest.raises(DadosInvalidos):
        services.criar_item(repo, nome, preco)


def test_obter_item_existente(repo_com_itens):
    item = services.obter_item(repo_com_itens, 1)

    assert item.nome == "Teclado"


def test_obter_item_inexistente_levanta_erro(repo):
    with pytest.raises(ItemNaoEncontrado):
        services.obter_item(repo, 999)


def test_remover_item_existente(repo_com_itens):
    services.remover_item(repo_com_itens, 1)

    assert repo_com_itens.buscar(1) is None
    assert len(repo_com_itens.listar()) == 1


def test_remover_item_inexistente_levanta_erro(repo):
    with pytest.raises(ItemNaoEncontrado):
        services.remover_item(repo, 999)


def test_listar_itens(repo_com_itens):
    itens = repo_com_itens.listar()

    assert len(itens) == 2
    assert [item.nome for item in itens] == ["Teclado", "Monitor"]
