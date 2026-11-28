from datetime import datetime, timezone

import pytest

from app.models.almoxarifado import AlmoxarifadoORM
from app.models.enums import PapelUsuario, TipoMovimentacao, UnidadeMedida
from app.models.movimentacao import MovimentacaoORM
from app.models.produto import ProdutoORM
from app.models.usuario import UsuarioORM

PRODUTO_PADRAO = {
    "almoxarifado_id": 1,
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "categoria": "Fixadores",
    "unidade": UnidadeMedida.UNIDADE,
    "descricao": "M8 x 40mm",
    "estoque_minimo": 50,
}


class RepositorioDeProdutosFalso:
    """Dublê em memória, para os testes unitários rodarem sem banco."""

    def __init__(self) -> None:
        self._produtos: dict[int, ProdutoORM] = {}
        self._proximo_id = 1

    def adicionar(self, **campos) -> ProdutoORM:
        produto = ProdutoORM(id=self._proximo_id, **campos)
        produto.movimentacoes = []
        self._produtos[produto.id] = produto
        self._proximo_id += 1
        return produto

    def buscar(self, produto_id: int) -> ProdutoORM | None:
        return self._produtos.get(produto_id)

    def buscar_por_codigo(self, codigo: str) -> ProdutoORM | None:
        return next((p for p in self._produtos.values() if p.codigo == codigo), None)

    def listar(
        self, almoxarifado_id=None, categoria=None, apenas_abaixo_do_minimo=False
    ) -> list[ProdutoORM]:
        produtos = sorted(self._produtos.values(), key=lambda p: p.nome)
        if almoxarifado_id is not None:
            produtos = [p for p in produtos if p.almoxarifado_id == almoxarifado_id]
        if categoria:
            produtos = [p for p in produtos if p.categoria == categoria]
        if apenas_abaixo_do_minimo:
            produtos = [p for p in produtos if p.saldo < p.estoque_minimo]
        return produtos

    def categorias(self, almoxarifado_id=None) -> list[str]:
        produtos = self._produtos.values()
        if almoxarifado_id is not None:
            produtos = [p for p in produtos if p.almoxarifado_id == almoxarifado_id]
        return sorted({p.categoria for p in produtos})

    def atualizar(self, produto: ProdutoORM, **campos) -> ProdutoORM:
        for campo, valor in campos.items():
            setattr(produto, campo, valor)
        return produto

    def remover(self, produto: ProdutoORM) -> None:
        del self._produtos[produto.id]

    def tem_movimentacoes(self, produto: ProdutoORM) -> bool:
        return len(produto.movimentacoes) > 0


class RepositorioDeMovimentacoesFalso:
    def __init__(self) -> None:
        self._movimentacoes: list[MovimentacaoORM] = []
        self._proximo_id = 1

    def registrar(
        self, produto, tipo, quantidade, responsavel, observacao, requerente="", destino=""
    ) -> MovimentacaoORM:
        movimentacao = MovimentacaoORM(
            id=self._proximo_id,
            produto_id=produto.id,
            tipo=tipo,
            quantidade=quantidade,
            responsavel=responsavel,
            observacao=observacao,
            requerente=requerente,
            destino=destino,
            criada_em=datetime.now(timezone.utc),
        )
        self._movimentacoes.append(movimentacao)
        self._proximo_id += 1

        if tipo is TipoMovimentacao.ENTRADA:
            produto.saldo += quantidade
        else:
            produto.saldo -= quantidade

        produto.movimentacoes.append(movimentacao)
        return movimentacao

    def listar_do_produto(self, produto_id: int) -> list[MovimentacaoORM]:
        return [m for m in reversed(self._movimentacoes) if m.produto_id == produto_id]


USUARIO_PADRAO = {
    "nome": "Davi",
    "email": "davi@almox.com",
    "setor": "TI",
    "senha": "senha123",
}


class RepositorioDeUsuariosFalso:
    def __init__(self) -> None:
        self._usuarios: dict[int, UsuarioORM] = {}
        self._proximo_id = 1

    def adicionar(
        self,
        nome: str,
        email: str,
        setor: str,
        senha_hash: str,
        papel: PapelUsuario = PapelUsuario.EMPREGADO,
    ) -> UsuarioORM:
        usuario = UsuarioORM(
            id=self._proximo_id,
            nome=nome,
            email=email,
            setor=setor,
            senha_hash=senha_hash,
            papel=papel,
        )
        self._usuarios[usuario.id] = usuario
        self._proximo_id += 1
        return usuario

    def buscar(self, usuario_id: int) -> UsuarioORM | None:
        return self._usuarios.get(usuario_id)

    def buscar_por_email(self, email: str) -> UsuarioORM | None:
        return next((u for u in self._usuarios.values() if u.email == email), None)


@pytest.fixture
def repo_usuarios() -> RepositorioDeUsuariosFalso:
    return RepositorioDeUsuariosFalso()


@pytest.fixture
def repo() -> RepositorioDeProdutosFalso:
    return RepositorioDeProdutosFalso()


@pytest.fixture
def repo_movimentacoes() -> RepositorioDeMovimentacoesFalso:
    return RepositorioDeMovimentacoesFalso()


@pytest.fixture
def produto(repo):
    """Produto já cadastrado, saldo zero."""
    return repo.adicionar(**PRODUTO_PADRAO, saldo=0)


ALMOXARIFADO_PADRAO = {
    "nome": "Central",
    "local": "Galpao A",
}


class RepositorioDeAlmoxarifadosFalso:
    def __init__(self) -> None:
        self._almoxarifados: dict[int, AlmoxarifadoORM] = {}
        self._proximo_id = 1
        self._produtos_por_almoxarifado: dict[int, int] = {}

    def adicionar(self, **campos) -> AlmoxarifadoORM:
        almoxarifado = AlmoxarifadoORM(id=self._proximo_id, **campos)
        self._almoxarifados[almoxarifado.id] = almoxarifado
        self._proximo_id += 1
        return almoxarifado

    def buscar(self, almoxarifado_id: int):
        return self._almoxarifados.get(almoxarifado_id)

    def buscar_por_nome(self, nome: str):
        alvo = nome.lower()
        return next((a for a in self._almoxarifados.values() if a.nome.lower() == alvo), None)

    def listar(self, apenas_ativos: bool = False):
        itens = sorted(self._almoxarifados.values(), key=lambda a: a.nome)
        return [a for a in itens if a.ativo] if apenas_ativos else itens

    def atualizar(self, almoxarifado, **campos):
        for campo, valor in campos.items():
            setattr(almoxarifado, campo, valor)
        return almoxarifado

    def remover(self, almoxarifado) -> None:
        del self._almoxarifados[almoxarifado.id]

    def contar_produtos(self, almoxarifado_id: int) -> int:
        return self._produtos_por_almoxarifado.get(almoxarifado_id, 0)

    def resumo(self, almoxarifado_id: int):
        return (self.contar_produtos(almoxarifado_id), 0, 0)


@pytest.fixture
def repo_almoxarifados() -> RepositorioDeAlmoxarifadosFalso:
    return RepositorioDeAlmoxarifadosFalso()
