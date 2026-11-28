from app.errors import (
    AlmoxarifadoComProdutos,
    AlmoxarifadoNaoEncontrado,
    DadosInvalidos,
    NomeDeAlmoxarifadoJaExiste,
)
from app.models.almoxarifado import AlmoxarifadoORM
from app.models.enums import PapelUsuario
from app.repositories.almoxarifado import RepositorioDeAlmoxarifados
from app.repositories.usuario import RepositorioDeUsuarios

NOME_MAXIMO = 80
LOCAL_MAXIMO = 120


def _validar(nome: str, local: str) -> tuple[str, str]:
    nome = (nome or "").strip()
    local = (local or "").strip()

    if not nome:
        raise DadosInvalidos("O nome do almoxarifado é obrigatório")
    if len(nome) > NOME_MAXIMO:
        raise DadosInvalidos(f"O nome deve ter até {NOME_MAXIMO} caracteres")
    if len(local) > LOCAL_MAXIMO:
        raise DadosInvalidos(f"O local deve ter até {LOCAL_MAXIMO} caracteres")

    return nome, local


def _validar_responsavel(
    repo_usuarios: RepositorioDeUsuarios | None, responsavel_id: int | None
) -> int | None:
    """O responsável, quando informado, precisa ser um empregado cadastrado."""
    if responsavel_id is None:
        return None

    usuario = None if repo_usuarios is None else repo_usuarios.buscar(responsavel_id)
    if usuario is None:
        raise DadosInvalidos("O responsável informado não é um operador cadastrado")

    # Quem cuida do dia a dia do depósito é o empregado; admin e gerente
    # administram o sistema, não ficam como responsáveis pelo estoque.
    if PapelUsuario(usuario.papel) is not PapelUsuario.EMPREGADO:
        raise DadosInvalidos("O responsável do almoxarifado deve ser um empregado")

    return responsavel_id


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
    responsavel_id: int | None = None,
    ativo: bool = True,
    repo_usuarios: RepositorioDeUsuarios | None = None,
) -> AlmoxarifadoORM:
    nome, local = _validar(nome, local)
    _garantir_nome_livre(repo, nome)
    responsavel_id = _validar_responsavel(repo_usuarios, responsavel_id)
    return repo.adicionar(nome=nome, local=local, responsavel_id=responsavel_id, ativo=ativo)


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
                "responsavel_id": almoxarifado.responsavel_id,
                "responsavel_nome": almoxarifado.responsavel_nome,
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
    responsavel_id: int | None = None,
    ativo: bool | None = None,
    repo_usuarios: RepositorioDeUsuarios | None = None,
) -> AlmoxarifadoORM:
    almoxarifado = obter_almoxarifado(repo, almoxarifado_id)

    novo_nome = almoxarifado.nome if nome is None else nome
    novo_local = almoxarifado.local if local is None else local
    novo_responsavel = almoxarifado.responsavel_id if responsavel_id is None else responsavel_id
    novo_ativo = almoxarifado.ativo if ativo is None else ativo

    novo_nome, novo_local = _validar(novo_nome, novo_local)
    _garantir_nome_livre(repo, novo_nome, almoxarifado_id)
    novo_responsavel = _validar_responsavel(repo_usuarios, novo_responsavel)

    return repo.atualizar(
        almoxarifado,
        nome=novo_nome,
        local=novo_local,
        responsavel_id=novo_responsavel,
        ativo=novo_ativo,
    )


def remover_almoxarifado(repo: RepositorioDeAlmoxarifados, almoxarifado_id: int) -> None:
    almoxarifado = obter_almoxarifado(repo, almoxarifado_id)
    if repo.contar_produtos(almoxarifado_id) > 0:
        raise AlmoxarifadoComProdutos(almoxarifado_id)
    repo.remover(almoxarifado)
