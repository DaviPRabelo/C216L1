NOVO = {"nome": "Obras", "local": "Patio 2", "responsavel": "Ana"}

PRODUTO = {
    "almoxarifado_id": 1,
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "categoria": "Fixadores",
    "unidade": "UN",
    "estoque_minimo": 50,
}


def test_listar_traz_o_deposito_padrao_com_resumo(client):
    resposta = client.get("/almoxarifados")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo[0]["nome"] == "Central"
    assert corpo[0]["total_produtos"] == 0
    assert corpo[0]["unidades_em_estoque"] == 0


def test_resumo_acompanha_os_produtos(client):
    client.post("/produtos", json=PRODUTO)
    client.post(
        "/produtos/1/movimentacoes",
        json={"tipo": "ENTRADA", "quantidade": 100, "responsavel": "Davi"},
    )

    central = client.get("/almoxarifados").json()[0]

    assert central["total_produtos"] == 1
    assert central["unidades_em_estoque"] == 100
    assert central["produtos_em_falta"] == 0


def test_criar_almoxarifado(client):
    resposta = client.post("/almoxarifados", json=NOVO)

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Obras"


def test_criar_com_nome_repetido_retorna_409(client):
    assert client.post("/almoxarifados", json={"nome": "Central"}).status_code == 409


def test_criar_sem_nome_retorna_422(client):
    assert client.post("/almoxarifados", json={"nome": ""}).status_code == 422


def test_obter_por_id(client):
    assert client.get("/almoxarifados/1").json()["nome"] == "Central"


def test_obter_inexistente_retorna_404(client):
    assert client.get("/almoxarifados/999").status_code == 404


def test_atualizar_parcialmente(client):
    resposta = client.patch("/almoxarifados/1", json={"responsavel": "Carla"})

    assert resposta.status_code == 200
    assert resposta.json()["responsavel"] == "Carla"
    assert resposta.json()["nome"] == "Central"


def test_desativar(client):
    client.patch("/almoxarifados/1", json={"ativo": False})

    assert client.get("/almoxarifados", params={"apenas_ativos": True}).json() == []


def test_remover(client):
    criado = client.post("/almoxarifados", json=NOVO).json()

    assert client.delete(f"/almoxarifados/{criado['id']}").status_code == 204
    assert client.get(f"/almoxarifados/{criado['id']}").status_code == 404


def test_remover_com_produtos_retorna_409(client):
    client.post("/produtos", json=PRODUTO)

    resposta = client.delete("/almoxarifados/1")

    assert resposta.status_code == 409


def test_produto_em_almoxarifado_inexistente_retorna_404(client):
    resposta = client.post("/produtos", json={**PRODUTO, "almoxarifado_id": 999})

    assert resposta.status_code == 404


def test_listar_produtos_filtra_por_almoxarifado(client):
    outro = client.post("/almoxarifados", json=NOVO).json()
    client.post("/produtos", json=PRODUTO)
    client.post(
        "/produtos",
        json={**PRODUTO, "almoxarifado_id": outro["id"], "codigo": "LUV-001", "nome": "Luva"},
    )

    da_central = client.get("/produtos", params={"almoxarifado_id": 1}).json()

    assert [p["nome"] for p in da_central] == ["Parafuso sextavado"]
