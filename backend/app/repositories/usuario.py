from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import PapelUsuario
from app.models.usuario import UsuarioORM


class RepositorioDeUsuarios:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(
        self,
        nome: str,
        email: str,
        setor: str,
        senha_hash: str,
        papel: PapelUsuario = PapelUsuario.EMPREGADO,
    ) -> UsuarioORM:
        usuario = UsuarioORM(
            nome=nome, email=email, setor=setor, senha_hash=senha_hash, papel=papel
        )
        self._sessao.add(usuario)
        self._sessao.commit()
        self._sessao.refresh(usuario)
        return usuario

    def buscar(self, usuario_id: int) -> UsuarioORM | None:
        return self._sessao.get(UsuarioORM, usuario_id)

    def buscar_por_email(self, email: str) -> UsuarioORM | None:
        return self._sessao.scalars(select(UsuarioORM).where(UsuarioORM.email == email)).first()

    def listar(self) -> list[UsuarioORM]:
        return list(self._sessao.scalars(select(UsuarioORM).order_by(UsuarioORM.nome)))
