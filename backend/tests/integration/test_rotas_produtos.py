PRODUTO = {
    "almoxarifado_id": 1,
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "descricao": "M8 x 40mm",
    "categoria": "Fixadores",
    "unidade": "UN",
    "estoque_minimo": 50,
}


def test_saude(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["servico"] == "almoxarifado"


def test_criar_produto(client):
    resposta = client.post("/produtos", json=PRODUTO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["codigo"] == "PAR-001"
    assert corpo["saldo"] == 0
    assert corpo["abaixo_do_minimo"] is True


def test_criar_produto_com_codigo_repetido(client):
    client.post("/produtos", json=PRODUTO)

    resposta = client.post("/produtos", json={**PRODUTO, "nome": "Outro"})

    assert resposta.status_code == 409
    assert "PAR-001" in resposta.json()["detail"]


def test_criar_produto_sem_nome(client):
    resposta = client.post("/produtos", json={**PRODUTO, "nome": ""})

    assert resposta.status_code == 422


def test_criar_produto_com_unidade_invalida(client):
    resposta = client.post("/produtos", json={**PRODUTO, "unidade": "TONELADA"})

    assert resposta.status_code == 422


def test_listar_produtos(client):
    client.post("/produtos", json=PRODUTO)
    client.post("/produtos", json={**PRODUTO, "codigo": "LUV-001", "nome": "Luva"})

    resposta = client.get("/produtos")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_listar_filtrando_por_categoria(client):
    client.post("/produtos", json=PRODUTO)
    client.post(
        "/produtos",
        json={**PRODUTO, "codigo": "LUV-001", "nome": "Luva", "categoria": "EPI"},
    )

    resposta = client.get("/produtos", params={"categoria": "EPI"})

    assert [p["nome"] for p in resposta.json()] == ["Luva"]


def test_listar_apenas_abaixo_do_minimo(client):
    criado = client.post("/produtos", json=PRODUTO).json()
    client.post(
        "/produtos",
        json={**PRODUTO, "codigo": "LUV-001", "nome": "Luva", "estoque_minimo": 5},
    )
    client.post(
        f"/produtos/{criado['id']}/movimentacoes",
        json={"tipo": "ENTRADA", "quantidade": 100, "responsavel": "Davi"},
    )

    resposta = client.get("/produtos", params={"abaixo_do_minimo": True})

    assert [p["nome"] for p in resposta.json()] == ["Luva"]


def test_estoque_minimo_zero_nunca_entra_no_alerta(client):
    client.post("/produtos", json={**PRODUTO, "estoque_minimo": 0})

    resposta = client.get("/produtos", params={"abaixo_do_minimo": True})

    assert resposta.json() == []


def test_listar_categorias(client):
    client.post("/produtos", json=PRODUTO)
    client.post(
        "/produtos",
        json={**PRODUTO, "codigo": "LUV-001", "nome": "Luva", "categoria": "EPI"},
    )

    resposta = client.get("/produtos/categorias")

    assert resposta.json() == ["EPI", "Fixadores"]


def test_obter_produto(client):
    criado = client.post("/produtos", json=PRODUTO).json()

    resposta = client.get(f"/produtos/{criado['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["codigo"] == "PAR-001"


def test_obter_produto_inexistente(client):
    assert client.get("/produtos/999999").status_code == 404


def test_substituir_produto(client):
    criado = client.post("/produtos", json=PRODUTO).json()

    resposta = client.put(
        f"/produtos/{criado['id']}", json={**PRODUTO, "nome": "Parafuso M10", "estoque_minimo": 10}
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Parafuso M10"
    assert resposta.json()["estoque_minimo"] == 10


def test_atualizar_parcialmente(client):
    criado = client.post("/produtos", json=PRODUTO).json()

    resposta = client.patch(f"/produtos/{criado['id']}", json={"estoque_minimo": 5})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estoque_minimo"] == 5
    assert corpo["codigo"] == "PAR-001"
    assert corpo["nome"] == "Parafuso sextavado"


def test_atualizar_com_codigo_de_outro(client):
    primeiro = client.post("/produtos", json=PRODUTO).json()
    client.post("/produtos", json={**PRODUTO, "codigo": "LUV-001", "nome": "Luva"})

    resposta = client.patch(f"/produtos/{primeiro['id']}", json={"codigo": "LUV-001"})

    assert resposta.status_code == 409


def test_remover_produto(client):
    criado = client.post("/produtos", json=PRODUTO).json()

    resposta = client.delete(f"/produtos/{criado['id']}")

    assert resposta.status_code == 204
    assert client.get(f"/produtos/{criado['id']}").status_code == 404


def test_remover_produto_com_movimentacoes(client):
    criado = client.post("/produtos", json=PRODUTO).json()
    client.post(
        f"/produtos/{criado['id']}/movimentacoes",
        json={"tipo": "ENTRADA", "quantidade": 10, "responsavel": "Davi"},
    )

    resposta = client.delete(f"/produtos/{criado['id']}")

    assert resposta.status_code == 409
    assert "histórico" in resposta.json()["detail"]


PNG_MINIMO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="


def test_criar_produto_com_foto(client):
    resposta = client.post("/produtos", json={**PRODUTO, "foto": PNG_MINIMO})

    assert resposta.status_code == 201
    assert resposta.json()["foto"] == PNG_MINIMO


def test_criar_produto_com_arquivo_que_nao_e_imagem(client):
    resposta = client.post(
        "/produtos", json={**PRODUTO, "foto": "data:application/pdf;base64,AAAA"}
    )

    assert resposta.status_code == 422


def test_foto_sobrevive_a_consulta(client):
    criado = client.post("/produtos", json={**PRODUTO, "foto": PNG_MINIMO}).json()

    lido = client.get(f"/produtos/{criado['id']}").json()

    assert lido["foto"] == PNG_MINIMO


def test_listar_categorias_disponiveis(client):
    resposta = client.get("/produtos/categorias/disponiveis")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "Fixadores" in corpo
    assert "EPI" in corpo
    assert len(corpo) == 9


def test_criar_produto_com_categoria_fora_da_lista_retorna_422(client):
    resposta = client.post("/produtos", json={**PRODUTO, "categoria": "Inventada"})

    assert resposta.status_code == 422
