from sqlalchemy.orm import sessionmaker

from app.models.item import ItemORM


def test_raiz_responde(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {"message": "API Prática 1 C216"}


def test_post_cria_item(client):
    resposta = client.post("/itens", json={"nome": "Teclado", "preco": 150.0})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] > 0
    assert corpo["nome"] == "Teclado"
    assert corpo["preco"] == 150.0


def test_post_com_dados_invalidos_retorna_422(client):
    resposta = client.post("/itens", json={"nome": "", "preco": 10.0})

    assert resposta.status_code == 422


def test_get_lista_itens(client, repo):
    repo.adicionar("Teclado", 150.0)
    repo.adicionar("Monitor", 900.0)

    resposta = client.get("/itens")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_get_lista_com_query_parameter(client, repo):
    repo.adicionar("Teclado", 150.0)
    repo.adicionar("Monitor", 900.0)

    resposta = client.get("/itens", params={"nome_contem": "tecl"})

    assert resposta.status_code == 200
    assert [item["nome"] for item in resposta.json()] == ["Teclado"]


def test_get_item_por_id(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.get(f"/itens/{item.id}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Teclado"


def test_get_item_inexistente_retorna_404(client):
    resposta = client.get("/itens/999999")

    assert resposta.status_code == 404


def test_put_substitui_item(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.put(
        f"/itens/{item.id}", json={"nome": "Teclado Mecânico", "preco": 400.0}
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"id": item.id, "nome": "Teclado Mecânico", "preco": 400.0}


def test_put_em_item_inexistente_retorna_404(client):
    resposta = client.put("/itens/999999", json={"nome": "Teclado", "preco": 150.0})

    assert resposta.status_code == 404


def test_put_com_dados_invalidos_retorna_422(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.put(f"/itens/{item.id}", json={"nome": "Teclado", "preco": -1.0})

    assert resposta.status_code == 422


def test_patch_atualiza_apenas_o_campo_enviado(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.patch(f"/itens/{item.id}", json={"preco": 199.9})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["preco"] == 199.9
    assert corpo["nome"] == "Teclado"


def test_patch_em_item_inexistente_retorna_404(client):
    resposta = client.patch("/itens/999999", json={"preco": 10.0})

    assert resposta.status_code == 404


def test_patch_com_dados_invalidos_retorna_422(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.patch(f"/itens/{item.id}", json={"nome": "   "})

    assert resposta.status_code == 422


def test_delete_remove_item(client, repo):
    item = repo.adicionar("Teclado", 150.0)

    resposta = client.delete(f"/itens/{item.id}")

    assert resposta.status_code == 204
    assert client.get(f"/itens/{item.id}").status_code == 404


def test_delete_em_item_inexistente_retorna_404(client):
    resposta = client.delete("/itens/999999")

    assert resposta.status_code == 404


def test_dados_persistem_em_outra_sessao(client, engine_de_teste):
    """Prova que o dado foi ao banco, e não ficou só na sessão da requisição."""
    criado = client.post("/itens", json={"nome": "Teclado", "preco": 150.0}).json()

    Sessao = sessionmaker(bind=engine_de_teste)
    with Sessao() as outra_sessao:
        persistido = outra_sessao.get(ItemORM, criado["id"])

        assert persistido is not None
        assert persistido.nome == "Teclado"
        assert persistido.preco == 150.0
