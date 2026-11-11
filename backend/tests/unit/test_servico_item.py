import pytest

from app.errors import DadosInvalidos, ItemNaoEncontrado, NomeJaExiste
from app.services import item as services

VALIDO = {
    "nome": "Teclado",
    "descricao": "Mecânico",
    "categoria": "Periféricos",
    "quantidade": 2,
    "preco": 150.0,
}


def test_criar_item_valido(repo):
    item = services.criar_item(repo, **VALIDO)

    assert item.id == 1
    assert item.nome == "Teclado"
    assert item.categoria == "Periféricos"
    assert item.quantidade == 2
    assert item.preco == 150.0


def test_criar_item_remove_espacos_do_nome_e_da_descricao(repo):
    item = services.criar_item(repo, **{**VALIDO, "nome": "  Mouse  ", "descricao": "  sem fio  "})

    assert item.nome == "Mouse"
    assert item.descricao == "sem fio"


def test_ids_sao_sequenciais(repo):
    primeiro = services.criar_item(repo, **VALIDO)
    segundo = services.criar_item(repo, **{**VALIDO, "nome": "Mouse"})

    assert (primeiro.id, segundo.id) == (1, 2)


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("nome", "   "),
        ("nome", "a" * 61),
        ("descricao", "a" * 201),
        ("categoria", ""),
        ("categoria", "Automóveis"),
        ("quantidade", 0),
        ("quantidade", -1),
        ("quantidade", 10_000),
        ("preco", -0.01),
        ("preco", 1_000_001),
    ],
)
def test_criar_item_invalido_levanta_erro(repo, campo, valor):
    with pytest.raises(DadosInvalidos):
        services.criar_item(repo, **{**VALIDO, campo: valor})


def test_criar_item_com_nome_repetido_levanta_erro(repo):
    services.criar_item(repo, **VALIDO)

    with pytest.raises(NomeJaExiste):
        services.criar_item(repo, **{**VALIDO, "preco": 999.0})


def test_obter_item_existente(repo_com_itens):
    assert services.obter_item(repo_com_itens, 1).nome == "Teclado"


def test_obter_item_inexistente_levanta_erro(repo):
    with pytest.raises(ItemNaoEncontrado):
        services.obter_item(repo, 999)


def test_listar_com_filtro_por_nome(repo_com_itens):
    encontrados = services.listar_itens(repo_com_itens, "tecl")

    assert [item.nome for item in encontrados] == ["Teclado"]


def test_substituir_item(repo_com_itens):
    item = services.substituir_item(
        repo_com_itens, 1, "Teclado ABNT2", "novo", "Periféricos", 5, 280.0
    )

    assert item.nome == "Teclado ABNT2"
    assert item.quantidade == 5


def test_substituir_com_nome_de_outro_item_levanta_erro(repo_com_itens):
    with pytest.raises(NomeJaExiste):
        services.substituir_item(repo_com_itens, 1, "Monitor", "x", "Periféricos", 1, 10.0)


def test_substituir_mantendo_o_proprio_nome_funciona(repo_com_itens):
    item = services.substituir_item(
        repo_com_itens, 1, "Teclado", "atualizado", "Periféricos", 3, 170.0
    )

    assert item.descricao == "atualizado"


def test_atualizar_parcial_preserva_os_campos_nao_enviados(repo_com_itens):
    item = services.atualizar_item(repo_com_itens, 1, preco=199.9)

    assert item.preco == 199.9
    assert item.nome == "Teclado"
    assert item.categoria == "Periféricos"
    assert item.quantidade == 2


def test_remover_item_existente(repo_com_itens):
    services.remover_item(repo_com_itens, 1)

    assert repo_com_itens.buscar(1) is None


def test_remover_item_inexistente_levanta_erro(repo):
    with pytest.raises(ItemNaoEncontrado):
        services.remover_item(repo, 999)
