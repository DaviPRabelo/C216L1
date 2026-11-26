from app.errors import (
    AlmoxarifadoComProdutos,
    AlmoxarifadoNaoEncontrado,
    DadosInvalidos,
    NomeDeAlmoxarifadoJaExiste,
)
from app.models.almoxarifado import AlmoxarifadoORM
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados

NOME_MAXIMO = 80
LOCAL_MAXIMO = 120
RESPONSAVEL_MAXIMO = 100


def _validar(nome: str, local: str, responsavel: str) -> tuple[str, str, str]:
    nome = (nome or "").strip()
    local = (local or "").strip()
    responsavel = (responsavel or "").strip()

    if not nome:
        raise DadosInvalidos("O nome do almoxarifado é obrigatório")
    if len(nome) > NOME_MAXIMO:
        raise DadosInvalidos(f"O nome deve ter até {NOME_MAXIMO} caracteres")
    if len(local) > LOCAL_MAXIMO:
        raise DadosInvalidos(f"O local deve ter até {LOCAL_MAXIMO} caracteres")
    if len(responsavel) > RESPONSAVEL_MAXIMO:
        raise DadosInvalidos(f"O responsável deve ter até {RESPONSAVEL_MAXIMO} caracteres")

    return nome, local, responsavel


def _garantir_nome_livre(
    repo: RepositorioDeAlmoxarifados, nome: str, almoxarifado_id: int | None = None
) -> None:
    existente = repo.buscar_por_nome(nome)
    if existente is not None and existente.id != almoxarifado_id:
        raise NomeDeAlmoxarifadoJaExiste(nome)


def criar_almoxarifado(
    repo: RepositorioDeAlmoxarifados,
    nome: str,
    local: str = "",
    responsavel: str = "",
    ativo: bool = True,
) -> AlmoxarifadoORM:
    nome, local, responsavel = _validar(nome, local, responsavel)
    _garantir_nome_livre(repo, nome)
    return repo.adicionar(nome=nome, local=local, responsavel=responsavel, ativo=ativo)


def obter_almoxarifado(repo: RepositorioDeAlmoxarifados, almoxarifado_id: int) -> AlmoxarifadoORM:
    almoxarifado = repo.buscar(almoxarifado_id)
    if almoxarifado is None:
        raise AlmoxarifadoNaoEncontrado(almoxarifado_id)
    return almoxarifado


def listar_almoxarifados(
    repo: RepositorioDeAlmoxarifados, apenas_ativos: bool = False
) -> list[AlmoxarifadoORM]:
    return repo.listar(apenas_ativos)


def resumir_almoxarifados(
    repo: RepositorioDeAlmoxarifados, apenas_ativos: bool = False
) -> list[dict]:
    """Lista com os números do estoque de cada depósito."""
    resumos = []
    for almoxarifado in repo.listar(apenas_ativos):
        total, em_falta, unidades = repo.resumo(almoxarifado.id)
        resumos.append(
            {
                "id": almoxarifado.id,
                "nome": almoxarifado.nome,
                "local": almoxarifado.local,
                "responsavel": almoxarifado.responsavel,
                "ativo": almoxarifado.ativo,
                "total_produtos": total,
                "produtos_em_falta": em_falta,
                "unidades_em_estoque": unidades,
            }
        )
    return resumos


def atualizar_almoxarifado(
    repo: RepositorioDeAlmoxarifados,
    almoxarifado_id: int,
    nome: str | None = None,
    local: str | None = None,
    responsavel: str | None = None,
    ativo: bool | None = None,
) -> AlmoxarifadoORM:
    almoxarifado = obter_almoxarifado(repo, almoxarifado_id)

    novo_nome = almoxarifado.nome if nome is None else nome
    novo_local = almoxarifado.local if local is None else local
    novo_responsavel = almoxarifado.responsavel if responsavel is None else responsavel
    novo_ativo = almoxarifado.ativo if ativo is None else ativo

    novo_nome, novo_local, novo_responsavel = _validar(novo_nome, novo_local, novo_responsavel)
    _garantir_nome_livre(repo, novo_nome, almoxarifado_id)

    return repo.atualizar(
        almoxarifado,
        nome=novo_nome,
        local=novo_local,
        responsavel=novo_responsavel,
        ativo=novo_ativo,
    )


def remover_almoxarifado(repo: RepositorioDeAlmoxarifados, almoxarifado_id: int) -> None:
    almoxarifado = obter_almoxarifado(repo, almoxarifado_id)
    if repo.contar_produtos(almoxarifado_id) > 0:
        raise AlmoxarifadoComProdutos(almoxarifado_id)
    repo.remover(almoxarifado)
