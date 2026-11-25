import bcrypt

# O bcrypt trunca silenciosamente acima de 72 bytes; recusamos antes disso.
SENHA_MAXIMA = 72


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def conferir_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_armazenado.encode())
    except ValueError:
        return False