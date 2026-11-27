class ErroDeDominio(Exception):
    """Erro base da aplicação."""


class DadosInvalidos(ErroDeDominio):
    pass


class ProdutoNaoEncontrado(ErroDeDominio):
    def __init__(self, produto_id: int):
        self.produto_id = produto_id
        super().__init__(f"Produto {produto_id} não encontrado")


class CodigoJaExiste(ErroDeDominio):
    def __init__(self, codigo: str):
        self.codigo = codigo
        super().__init__(f"Já existe um produto com o código {codigo}")


class SaldoInsuficiente(ErroDeDominio):
    def __init__(self, disponivel: int, solicitado: int, unidade: str):
        self.disponivel = disponivel
        self.solicitado = solicitado
        super().__init__(
            f"Saldo insuficiente: disponível {disponivel} {unidade}, "
            f"solicitado {solicitado} {unidade}"
        )


class ProdutoComMovimentacoes(ErroDeDominio):
    def __init__(self, produto_id: int):
        self.produto_id = produto_id
        super().__init__(
            "Não é possível excluir um produto que já teve movimentações. "
            "O histórico precisa ser preservado."
        )


class CredenciaisInvalidas(ErroDeDominio):
    def __init__(self):
        super().__init__("E-mail ou senha incorretos")


class EmailJaExiste(ErroDeDominio):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Já existe uma conta com o e-mail {email}")


class AlmoxarifadoNaoEncontrado(ErroDeDominio):
    def __init__(self, almoxarifado_id: int):
        self.almoxarifado_id = almoxarifado_id
        super().__init__(f"Almoxarifado {almoxarifado_id} não encontrado")


class NomeDeAlmoxarifadoJaExiste(ErroDeDominio):
    def __init__(self, nome: str):
        self.nome = nome
        super().__init__(f"Já existe um almoxarifado chamado {nome}")


class AlmoxarifadoComProdutos(ErroDeDominio):
    def __init__(self, almoxarifado_id: int):
        self.almoxarifado_id = almoxarifado_id
        super().__init__(
            "Não é possível excluir um almoxarifado que ainda tem produtos cadastrados."
        )


class InventarioNaoEncontrado(ErroDeDominio):
    def __init__(self, inventario_id: int):
        self.inventario_id = inventario_id
        super().__init__(f"Inventário {inventario_id} não encontrado")


class JaExisteInventarioAberto(ErroDeDominio):
    def __init__(self, inventario_id: int):
        self.inventario_id = inventario_id
        super().__init__(
            f"Já existe um inventário aberto neste almoxarifado (nº {inventario_id}). "
            "Feche-o antes de abrir outro."
        )


class InventarioJaFechado(ErroDeDominio):
    def __init__(self, inventario_id: int):
        self.inventario_id = inventario_id
        super().__init__("Este inventário já foi fechado e não aceita alterações")


class ContagemIncompleta(ErroDeDominio):
    def __init__(self, faltando: int):
        self.faltando = faltando
        super().__init__(f"Ainda faltam {faltando} itens para contar antes de fechar o inventário")


class ItemDeInventarioNaoEncontrado(ErroDeDominio):
    def __init__(self, produto_id: int):
        self.produto_id = produto_id
        super().__init__(f"O produto {produto_id} não faz parte deste inventário")
