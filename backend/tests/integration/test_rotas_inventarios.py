PRODUTO = {
    "almoxarifado_id": 1,
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "categoria": "Fixadores",
    "unidade": "UN",
    "estoque_minimo": 50,
}


def criar_produto(client, **extras):
    return client.post("/produtos", json={**PRODUTO, **extras}).json()


def abastecer(client, produto_id, quantidade):
    client.post(
        f"/produtos/{produto_id}/movimentacoes",
        json={"tipo": "ENTRADA", "quantidade": quantidade, "responsavel": "Davi"},
    )


def abrir(client, responsavel="Davi"):
    return client.post("/inventarios", json={"almoxarifado_id": 1, "responsavel": responsavel})


def test_abrir_congela_o_saldo_de_cada_produto(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 100)

    resposta = abrir(client)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "ABERTO"
    assert corpo["responsavel"] == "Davi"
    assert len(corpo["itens"]) == 1
    assert corpo["itens"][0]["saldo_sistema"] == 100
    assert corpo["itens"][0]["quantidade_contada"] is None
    assert corpo["itens"][0]["divergencia"] is None


def test_item_traz_os_dados_do_produto(client):
    criar_produto(client)

    item = abrir(client).json()["itens"][0]

    assert item["produto_codigo"] == "PAR-001"
    assert item["produto_nome"] == "Parafuso sextavado"
    assert item["unidade"] == "UN"


def test_abrir_sem_produtos_retorna_422(client):
    resposta = abrir(client)

    assert resposta.status_code == 422
    assert "produtos" in resposta.json()["detail"]


def test_abrir_sem_responsavel_retorna_422(client):
    criar_produto(client)

    assert abrir(client, responsavel="").status_code == 422


def test_abrir_com_outro_aberto_retorna_409(client):
    criar_produto(client)
    abrir(client)

    resposta = abrir(client)

    assert resposta.status_code == 409
    assert "já existe um inventário aberto" in resposta.json()["detail"].lower()


def test_abrir_em_almoxarifado_inexistente_retorna_404(client):
    resposta = client.post("/inventarios", json={"almoxarifado_id": 999, "responsavel": "Davi"})

    assert resposta.status_code == 404


def test_contagem_igual_ao_sistema_nao_gera_divergencia(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 100)
    inventario = abrir(client).json()

    resposta = client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 100},
    )

    item = resposta.json()["itens"][0]
    assert item["quantidade_contada"] == 100
    assert item["divergencia"] == 0
    assert resposta.json()["itens_divergentes"] == 0


def test_contagem_menor_aponta_falta(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 100)
    inventario = abrir(client).json()

    corpo = client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 93},
    ).json()

    assert corpo["itens"][0]["divergencia"] == -7
    assert corpo["itens_divergentes"] == 1


def test_contagem_maior_aponta_sobra(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 100)
    inventario = abrir(client).json()

    corpo = client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 105},
    ).json()

    assert corpo["itens"][0]["divergencia"] == 5


def test_contar_produto_fora_do_inventario_retorna_404(client):
    criar_produto(client)
    inventario = abrir(client).json()

    resposta = client.patch(
        f"/inventarios/{inventario['id']}/itens/999", json={"quantidade_contada": 1}
    )

    assert resposta.status_code == 404


def test_quantidade_negativa_retorna_422(client):
    produto = criar_produto(client)
    inventario = abrir(client).json()

    resposta = client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": -1},
    )

    assert resposta.status_code == 422


def test_fechar_com_itens_por_contar_retorna_409(client):
    criar_produto(client)
    criar_produto(client, codigo="LUV-001", nome="Luva")
    inventario = abrir(client).json()

    resposta = client.post(f"/inventarios/{inventario['id']}/fechar")

    assert resposta.status_code == 409
    assert "faltam 2" in resposta.json()["detail"]


def test_fechar_depois_de_contar_tudo(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 40)
    inventario = abrir(client).json()
    client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 38},
    )

    resposta = client.post(f"/inventarios/{inventario['id']}/fechar")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "FECHADO"
    assert corpo["itens_contados"] == 1
    assert corpo["itens_divergentes"] == 1


def test_contagem_zero_conta_como_contado(client):
    produto = criar_produto(client)
    abastecer(client, produto["id"], 10)
    inventario = abrir(client).json()

    client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 0},
    )
    resposta = client.post(f"/inventarios/{inventario['id']}/fechar")

    assert resposta.status_code == 200
    assert resposta.json()["itens"][0]["divergencia"] == -10


def test_inventario_fechado_nao_aceita_contagem(client):
    produto = criar_produto(client)
    inventario = abrir(client).json()
    client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 5},
    )
    client.post(f"/inventarios/{inventario['id']}/fechar")

    resposta = client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 9},
    )

    assert resposta.status_code == 409
    assert "já foi fechado" in resposta.json()["detail"]


def test_fechar_duas_vezes_retorna_409(client):
    produto = criar_produto(client)
    inventario = abrir(client).json()
    client.patch(
        f"/inventarios/{inventario['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 0},
    )
    client.post(f"/inventarios/{inventario['id']}/fechar")

    assert client.post(f"/inventarios/{inventario['id']}/fechar").status_code == 409


def test_fechar_libera_a_abertura_de_outro(client):
    produto = criar_produto(client)
    primeiro = abrir(client).json()
    client.patch(
        f"/inventarios/{primeiro['id']}/itens/{produto['id']}",
        json={"quantidade_contada": 0},
    )
    client.post(f"/inventarios/{primeiro['id']}/fechar")

    assert abrir(client).status_code == 201


def test_listar_filtra_por_almoxarifado(client):
    criar_produto(client)
    abrir(client)

    assert len(client.get("/inventarios", params={"almoxarifado_id": 1}).json()) == 1
    assert client.get("/inventarios", params={"almoxarifado_id": 999}).json() == []


def test_obter_inventario_inexistente_retorna_404(client):
    assert client.get("/inventarios/999").status_code == 404
