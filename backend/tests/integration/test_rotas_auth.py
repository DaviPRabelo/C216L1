USUARIO = {
    "nome": "Davi",
    "email": "davi@almox.com",
    "setor": "TI",
    "senha": "senha123",
}


def test_registrar(client):
    resposta = client.post("/auth/registrar", json=USUARIO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == "davi@almox.com"
    assert corpo["setor"] == "TI"


def test_resposta_nunca_expoe_a_senha(client):
    resposta = client.post("/auth/registrar", json=USUARIO)

    corpo = resposta.json()
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_registrar_email_repetido_retorna_409(client):
    client.post("/auth/registrar", json=USUARIO)

    resposta = client.post("/auth/registrar", json={**USUARIO, "nome": "Outro"})

    assert resposta.status_code == 409


def test_registrar_com_senha_curta_retorna_422(client):
    assert client.post("/auth/registrar", json={**USUARIO, "senha": "123"}).status_code == 422


def test_registrar_com_email_invalido_retorna_422(client):
    assert client.post("/auth/registrar", json={**USUARIO, "email": "abc"}).status_code == 422


def test_login(client):
    client.post("/auth/registrar", json=USUARIO)

    resposta = client.post(
        "/auth/login", json={"email": "davi@almox.com", "senha": "senha123"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Davi"


def test_login_aceita_email_em_maiusculo(client):
    client.post("/auth/registrar", json=USUARIO)

    resposta = client.post(
        "/auth/login", json={"email": "DAVI@ALMOX.COM", "senha": "senha123"}
    )

    assert resposta.status_code == 200


def test_login_com_senha_errada_retorna_401(client):
    client.post("/auth/registrar", json=USUARIO)

    resposta = client.post("/auth/login", json={"email": "davi@almox.com", "senha": "errada"})

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha incorretos"


def test_login_com_email_inexistente_retorna_401(client):
    resposta = client.post("/auth/login", json={"email": "x@y.com", "senha": "senha123"})

    assert resposta.status_code == 401