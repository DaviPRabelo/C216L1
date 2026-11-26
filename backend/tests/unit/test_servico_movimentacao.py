import pytest

from app.errors import DadosInvalidos, ProdutoNaoEncontrado, SaldoInsuficiente
from app.models.enums import TipoMovimentacao
from app.services import movimentacao as servico

ENTRADA = TipoMovimentacao.ENTRADA
SAIDA = TipoMovimentacao.SAIDA


def registrar(
    repo,
    repo_mov,
    produto_id,
    tipo,
    quantidade,
    responsavel="Davi",
    observacao="",
    requerente=None,
    destino=None,
):
    """Preenche requerente e destino por padrão nas saídas, que os exigem."""
    if tipo is SAIDA:
        requerente = "Maria" if requerente is None else requerente
        destino = "Manutenção" if destino is None else destino

    return servico.registrar_movimentacao(
        repo,
        repo_mov,
        produto_id,
        tipo=tipo,
        quantidade=quantidade,
        responsavel=responsavel,
        requerente=requerente or "",
        destino=destino or "",
        observacao=observacao,
    )


def test_entrada_aumenta_o_saldo(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 100)

    assert produto.saldo == 100


def test_saida_diminui_o_saldo(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 100)
    registrar(repo, repo_movimentacoes, produto.id, SAIDA, 30)

    assert produto.saldo == 70


def test_sequencia_de_movimentacoes_acumula(repo, repo_movimentacoes, produto):
    for quantidade in (50, 30, 20):
        registrar(repo, repo_movimentacoes, produto.id, ENTRADA, quantidade)
    registrar(repo, repo_movimentacoes, produto.id, SAIDA, 60)

    assert produto.saldo == 40


def test_saida_maior_que_o_saldo_e_recusada(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 70)

    with pytest.raises(SaldoInsuficiente) as erro:
        registrar(repo, repo_movimentacoes, produto.id, SAIDA, 500)

    assert erro.value.disponivel == 70
    assert erro.value.solicitado == 500
    assert "disponível 70 UN" in str(erro.value)


def test_saida_recusada_nao_altera_o_saldo(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 70)

    with pytest.raises(SaldoInsuficiente):
        registrar(repo, repo_movimentacoes, produto.id, SAIDA, 500)

    assert produto.saldo == 70
    assert len(repo_movimentacoes.listar_do_produto(produto.id)) == 1


def test_saida_exatamente_igual_ao_saldo_e_permitida(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 40)
    registrar(repo, repo_movimentacoes, produto.id, SAIDA, 40)

    assert produto.saldo == 0


def test_saida_de_produto_zerado_e_recusada(repo, repo_movimentacoes, produto):
    with pytest.raises(SaldoInsuficiente):
        registrar(repo, repo_movimentacoes, produto.id, SAIDA, 1)


@pytest.mark.parametrize("quantidade", [0, -1, -100, 1_000_000])
def test_quantidade_invalida(repo, repo_movimentacoes, produto, quantidade):
    with pytest.raises(DadosInvalidos):
        registrar(repo, repo_movimentacoes, produto.id, ENTRADA, quantidade)


@pytest.mark.parametrize("responsavel", ["", "   ", "R" * 101])
def test_responsavel_invalido(repo, repo_movimentacoes, produto, responsavel):
    with pytest.raises(DadosInvalidos):
        registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 10, responsavel=responsavel)


def test_observacao_longa_demais(repo, repo_movimentacoes, produto):
    with pytest.raises(DadosInvalidos):
        registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 10, observacao="O" * 201)


def test_movimentar_produto_inexistente(repo, repo_movimentacoes):
    with pytest.raises(ProdutoNaoEncontrado):
        registrar(repo, repo_movimentacoes, 999, ENTRADA, 10)


def test_entrada_resolve_o_alerta_de_estoque_minimo(repo, repo_movimentacoes, produto):
    assert produto.abaixo_do_minimo is True

    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 100)

    assert produto.abaixo_do_minimo is False


def test_saida_pode_reabrir_o_alerta(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 100)
    registrar(repo, repo_movimentacoes, produto.id, SAIDA, 60)

    assert produto.saldo == 40
    assert produto.abaixo_do_minimo is True


def test_historico_vem_do_mais_recente_para_o_mais_antigo(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 10, observacao="primeira")
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 20, observacao="segunda")

    historico = servico.listar_movimentacoes(repo, repo_movimentacoes, produto.id)

    assert [m.observacao for m in historico] == ["segunda", "primeira"]


def test_historico_de_produto_inexistente(repo, repo_movimentacoes):
    with pytest.raises(ProdutoNaoEncontrado):
        servico.listar_movimentacoes(repo, repo_movimentacoes, 999)


def test_saida_sem_requerente_e_recusada(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 50)

    with pytest.raises(DadosInvalidos, match="requerente"):
        registrar(repo, repo_movimentacoes, produto.id, SAIDA, 10, requerente="")


def test_saida_sem_destino_e_recusada(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 50)

    with pytest.raises(DadosInvalidos, match="destino"):
        registrar(repo, repo_movimentacoes, produto.id, SAIDA, 10, destino="")


def test_saida_registra_requerente_e_destino(repo, repo_movimentacoes, produto):
    registrar(repo, repo_movimentacoes, produto.id, ENTRADA, 50)

    saida = registrar(
        repo, repo_movimentacoes, produto.id, SAIDA, 10, requerente="Ana", destino="Oficina"
    )

    assert (saida.requerente, saida.destino) == ("Ana", "Oficina")


def test_entrada_ignora_requerente_e_destino(repo, repo_movimentacoes, produto):
    entrada = registrar(
        repo, repo_movimentacoes, produto.id, ENTRADA, 50, requerente="Ana", destino="Oficina"
    )

    assert (entrada.requerente, entrada.destino) == ("", "")
