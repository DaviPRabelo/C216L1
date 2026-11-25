from app.errors import DadosInvalidos, SaldoInsuficiente
from app.models.enums import TipoMovimentacao
from app.models.movimentacao import MovimentacaoORM
from app.repositories.movimentacao import RepositorioDeMovimentacoes
from app.repositories.produto import RepositorioDeProdutos
from app.services import produto as servico_produto

QUANTIDADE_MAXIMA = 999_999
RESPONSAVEL_MAXIMO = 100
OBSERVACAO_MAXIMA = 200


def registrar_movimentacao(
    repo_produtos: RepositorioDeProdutos,
    repo_movimentacoes: RepositorioDeMovimentacoes,
    produto_id: int,
    tipo: TipoMovimentacao,
    quantidade: int,
    responsavel: str,
    requerente: str = "",
    destino: str = "",
    observacao: str = "",
) -> MovimentacaoORM:
    produto = servico_produto.obter_produto(repo_produtos, produto_id)

    responsavel = (responsavel or "").strip()
    requerente = (requerente or "").strip()
    destino = (destino or "").strip()
    observacao = (observacao or "").strip()

    if tipo is TipoMovimentacao.SAIDA:
        if not requerente:
            raise DadosInvalidos("Toda saída precisa informar o requerente")
        if not destino:
            raise DadosInvalidos("Toda saída precisa informar o destino")
    else:
        # Entrada não tem requerente nem destino: o material está chegando.
        requerente = ""
        destino = ""

    if len(requerente) > 100:
        raise DadosInvalidos("O requerente deve ter até 100 caracteres")
    if len(destino) > 100:
        raise DadosInvalidos("O destino deve ter até 100 caracteres")

    if quantidade <= 0:
        raise DadosInvalidos("A quantidade deve ser maior que zero")
    if quantidade > QUANTIDADE_MAXIMA:
        raise DadosInvalidos(f"A quantidade não pode passar de {QUANTIDADE_MAXIMA}")
    if not responsavel:
        raise DadosInvalidos("O responsável é obrigatório")
    if len(responsavel) > RESPONSAVEL_MAXIMO:
        raise DadosInvalidos(f"O responsável deve ter até {RESPONSAVEL_MAXIMO} caracteres")
    if len(observacao) > OBSERVACAO_MAXIMA:
        raise DadosInvalidos(f"A observação deve ter até {OBSERVACAO_MAXIMA} caracteres")

    if tipo is TipoMovimentacao.SAIDA and quantidade > produto.saldo:
        raise SaldoInsuficiente(produto.saldo, quantidade, produto.unidade.value)

    return repo_movimentacoes.registrar(
        produto, tipo, quantidade, responsavel, observacao, requerente, destino
    )


def listar_movimentacoes(
    repo_produtos: RepositorioDeProdutos,
    repo_movimentacoes: RepositorioDeMovimentacoes,
    produto_id: int,
) -> list[MovimentacaoORM]:
    servico_produto.obter_produto(repo_produtos, produto_id)
    return repo_movimentacoes.listar_do_produto(produto_id)
