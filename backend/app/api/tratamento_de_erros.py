from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import (
    AlmoxarifadoComProdutos,
    AlmoxarifadoNaoEncontrado,
    CodigoJaExiste,
    ContagemIncompleta,
    CredenciaisInvalidas,
    DadosInvalidos,
    EmailJaExiste,
    ErroDeDominio,
    InventarioJaFechado,
    InventarioNaoEncontrado,
    ItemDeInventarioNaoEncontrado,
    JaExisteInventarioAberto,
    NomeDeAlmoxarifadoJaExiste,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
    SaldoInsuficiente,
)

STATUS_POR_ERRO: dict[type[ErroDeDominio], int] = {
    ProdutoNaoEncontrado: 404,
    InventarioNaoEncontrado: 404,
    ItemDeInventarioNaoEncontrado: 404,
    JaExisteInventarioAberto: 409,
    InventarioJaFechado: 409,
    ContagemIncompleta: 409,
    AlmoxarifadoNaoEncontrado: 404,
    NomeDeAlmoxarifadoJaExiste: 409,
    AlmoxarifadoComProdutos: 409,
    CodigoJaExiste: 409,
    ProdutoComMovimentacoes: 409,
    SaldoInsuficiente: 409,
    EmailJaExiste: 409,
    CredenciaisInvalidas: 401,
    DadosInvalidos: 422,
}


async def tratar_erro_de_dominio(_: Request, erro: Exception) -> JSONResponse:
    status = STATUS_POR_ERRO.get(type(erro), 400)
    return JSONResponse(status_code=status, content={"detail": str(erro)})


def registrar_tratadores(app: FastAPI) -> None:
    """Liga as exceções de domínio aos códigos HTTP correspondentes."""
    app.add_exception_handler(ErroDeDominio, tratar_erro_de_dominio)
