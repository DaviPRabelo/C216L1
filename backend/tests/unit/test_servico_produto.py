import pytest

from app.errors import (
    CodigoJaExiste,
    DadosInvalidos,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
)
from app.models.enums import TipoMovimentacao, UnidadeMedida
from app.services import produto as servico
from tests.conftest import PRODUTO_PADRAO


def test_criar_produto_valido(repo):
    criado = servico.criar_produto(repo, **PRODUTO_PADRAO)

    assert criado.id == 1
    assert criado.codigo == "PAR-001"
    assert criado.saldo == 0
    assert criado.abaixo_do_minimo is True


def test_codigo_e_normalizado_para_maiusculo(repo):
    criado = servico.criar_produto(repo, **{**PRODUTO_PADRAO, "codigo": "  par-002  "})

    assert criado.codigo == "PAR-002"


def test_produto_novo_nasce_abaixo_do_minimo(repo):
    criado = servico.criar_produto(repo, **{**PRODUTO_PADRAO, "estoque_minimo": 10})

    assert criado.saldo == 0
    assert criado.abaixo_do_minimo is True


def test_estoque_minimo_zero_nao_gera_alerta(repo):
    criado = servico.criar_produto(repo, **{**PRODUTO_PADRAO, "estoque_minimo": 0})

    assert criado.abaixo_do_minimo is False


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("codigo", ""),
        ("codigo", "   "),
        ("codigo", "X" * 21),
        ("nome", ""),
        ("nome", "N" * 101),
        ("descricao", "D" * 201),
        ("categoria", ""),
        ("categoria", "C" * 51),
        ("estoque_minimo", -1),
    ],
)
def test_criar_produto_invalido(repo, campo, valor):
    with pytest.raises(DadosInvalidos):
        servico.criar_produto(repo, **{**PRODUTO_PADRAO, campo: valor})


def test_codigo_duplicado_e_recusado(repo):
    servico.criar_produto(repo, **PRODUTO_PADRAO)

    with pytest.raises(CodigoJaExiste):
        servico.criar_produto(repo, **{**PRODUTO_PADRAO, "nome": "Outro"})


def test_codigo_duplicado_ignora_maiusculas(repo):
    servico.criar_produto(repo, **PRODUTO_PADRAO)

    with pytest.raises(CodigoJaExiste):
        servico.criar_produto(repo, **{**PRODUTO_PADRAO, "codigo": "par-001"})


def test_obter_produto_inexistente(repo):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.obter_produto(repo, 999)


def test_listar_filtra_por_categoria(repo):
    servico.criar_produto(repo, **PRODUTO_PADRAO)
    servico.criar_produto(
        repo, **{**PRODUTO_PADRAO, "codigo": "LUV-001", "nome": "Luva", "categoria": "EPI"}
    )

    encontrados = servico.listar_produtos(repo, categoria="EPI")

    assert [p.nome for p in encontrados] == ["Luva"]


def test_listar_filtra_apenas_abaixo_do_minimo(repo, repo_movimentacoes):
    from app.services import movimentacao as servico_mov

    abastecido = servico.criar_produto(repo, **PRODUTO_PADRAO)
    servico.criar_produto(
        repo, **{**PRODUTO_PADRAO, "codigo": "LUV-001", "nome": "Luva", "estoque_minimo": 5}
    )
    servico_mov.registrar_movimentacao(
        repo, repo_movimentacoes, abastecido.id, TipoMovimentacao.ENTRADA, 100, "Davi"
    )

    em_falta = servico.listar_produtos(repo, apenas_abaixo_do_minimo=True)

    assert [p.nome for p in em_falta] == ["Luva"]


def test_atualizar_preserva_campos_nao_enviados(repo, produto):
    atualizado = servico.atualizar_produto(repo, produto.id, nome="Parafuso M10")

    assert atualizado.nome == "Parafuso M10"
    assert atualizado.codigo == "PAR-001"
    assert atualizado.categoria == "Fixadores"


def test_atualizar_mantendo_o_proprio_codigo_funciona(repo, produto):
    atualizado = servico.atualizar_produto(repo, produto.id, codigo="PAR-001", nome="Novo")

    assert atualizado.nome == "Novo"


def test_atualizar_com_codigo_de_outro_produto_e_recusado(repo, produto):
    servico.criar_produto(repo, **{**PRODUTO_PADRAO, "codigo": "LUV-001", "nome": "Luva"})

    with pytest.raises(CodigoJaExiste):
        servico.atualizar_produto(repo, produto.id, codigo="LUV-001")


def test_atualizar_nao_expoe_o_saldo(repo, produto):
    with pytest.raises(TypeError):
        servico.atualizar_produto(repo, produto.id, saldo=999)


def test_remover_produto_sem_movimentacoes(repo, produto):
    servico.remover_produto(repo, produto.id)

    assert repo.buscar(produto.id) is None


def test_remover_produto_com_movimentacoes_e_recusado(repo, repo_movimentacoes, produto):
    from app.services import movimentacao as servico_mov

    servico_mov.registrar_movimentacao(
        repo, repo_movimentacoes, produto.id, TipoMovimentacao.ENTRADA, 10, "Davi"
    )

    with pytest.raises(ProdutoComMovimentacoes):
        servico.remover_produto(repo, produto.id)


def test_listar_categorias_sem_repeticao(repo):
    servico.criar_produto(repo, **PRODUTO_PADRAO)
    servico.criar_produto(repo, **{**PRODUTO_PADRAO, "codigo": "PAR-002", "nome": "Outro"})
    servico.criar_produto(
        repo, **{**PRODUTO_PADRAO, "codigo": "LUV-001", "nome": "Luva", "categoria": "EPI"}
    )

    assert servico.listar_categorias(repo) == ["EPI", "Fixadores"]


def test_unidade_invalida_e_barrada_pelo_enum():
    with pytest.raises(ValueError):
        UnidadeMedida("TONELADA")


PNG_MINIMO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="


def test_produto_nasce_sem_foto(repo):
    criado = servico.criar_produto(repo, **PRODUTO_PADRAO)

    assert criado.foto == ""


def test_aceita_foto_em_data_url(repo):
    criado = servico.criar_produto(repo, **PRODUTO_PADRAO, foto=PNG_MINIMO)

    assert criado.foto == PNG_MINIMO


def test_recusa_arquivo_que_nao_e_imagem(repo):
    with pytest.raises(DadosInvalidos, match="imagem"):
        servico.criar_produto(repo, **PRODUTO_PADRAO, foto="data:application/pdf;base64,AAAA")


def test_recusa_imagem_grande_demais(repo):
    enorme = "data:image/png;base64," + "A" * 700_000

    with pytest.raises(DadosInvalidos, match="grande"):
        servico.criar_produto(repo, **PRODUTO_PADRAO, foto=enorme)


def test_atualizar_preserva_a_foto_quando_nao_enviada(repo):
    criado = servico.criar_produto(repo, **PRODUTO_PADRAO, foto=PNG_MINIMO)

    atualizado = servico.atualizar_produto(repo, criado.id, nome="Outro nome")

    assert atualizado.foto == PNG_MINIMO


def test_atualizar_pode_remover_a_foto(repo):
    criado = servico.criar_produto(repo, **PRODUTO_PADRAO, foto=PNG_MINIMO)

    atualizado = servico.atualizar_produto(repo, criado.id, foto="")

    assert atualizado.foto == ""
