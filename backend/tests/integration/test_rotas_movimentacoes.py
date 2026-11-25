PRODUTO = {
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "categoria": "Fixadores",
    "unidade": "UN",
    "estoque_minimo": 50,
}


def criar_produto(client):
    return client.post("/produtos", json=PRODUTO).json()


def movimentar(client, produto_id, tipo, quantidade, responsavel="Davi", observacao=""):
    return client.post(
        f"/produtos/{produto_id}/movimentacoes",
        json={
            "tipo": tipo,
            "quantidade": quantidade,
            "responsavel": responsavel,
            "observacao": observacao,
        },
    )


def test_entrada_atualiza_o_saldo(client):
    produto = criar_produto(client)

    resposta = movimentar(client, produto["id"], "ENTRADA", 100)

    assert resposta.status_code == 201
    assert resposta.json()["tipo"] == "ENTRADA"
    assert client.get(f"/produtos/{produto['id']}").json()["saldo"] == 100


def test_saida_atualiza_o_saldo(client):
    produto = criar_produto(client)
    movimentar(client, produto["id"], "ENTRADA", 100)

    movimentar(client, produto["id"], "SAIDA", 30)

    assert client.get(f"/produtos/{produto['id']}").json()["saldo"] == 70


def test_saida_maior_que_o_saldo_retorna_409(client):
    produto = criar_produto(client)
    movimentar(client, produto["id"], "ENTRADA", 70)

    resposta = movimentar(client, produto["id"], "SAIDA", 500)

    assert resposta.status_code == 409
    assert "Saldo insuficiente" in resposta.json()["detail"]
    assert "disponível 70 UN" in resposta.json()["detail"]


def test_saida_recusada_nao_altera_o_saldo(client):
    produto = criar_produto(client)
    movimentar(client, produto["id"], "ENTRADA", 70)

    movimentar(client, produto["id"], "SAIDA", 500)

    assert client.get(f"/produtos/{produto['id']}").json()["saldo"] == 70
    assert len(client.get(f"/produtos/{produto['id']}/movimentacoes").json()) == 1


def test_quantidade_zero_retorna_422(client):
    produto = criar_produto(client)

    assert movimentar(client, produto["id"], "ENTRADA", 0).status_code == 422


def test_responsavel_vazio_retorna_422(client):
    produto = criar_produto(client)

    assert movimentar(client, produto["id"], "ENTRADA", 10, responsavel="").status_code == 422


def test_tipo_invalido_retorna_422(client):
    produto = criar_produto(client)

    assert movimentar(client, produto["id"], "DEVOLUCAO", 10).status_code == 422


def test_movimentar_produto_inexistente_retorna_404(client):
    assert movimentar(client, 999999, "ENTRADA", 10).status_code == 404


def test_historico_do_produto(client):
    produto = criar_produto(client)
    movimentar(client, produto["id"], "ENTRADA", 50, observacao="compra inicial")
    movimentar(client, produto["id"], "SAIDA", 20, observacao="requisicao 12")

    resposta = client.get(f"/produtos/{produto['id']}/movimentacoes")

    assert resposta.status_code == 200
    historico = resposta.json()
    assert [m["observacao"] for m in historico] == ["requisicao 12", "compra inicial"]
    assert historico[0]["criada_em"] is not None


def test_historico_de_produto_inexistente_retorna_404(client):
    assert client.get("/produtos/999999/movimentacoes").status_code == 404


def test_alerta_de_estoque_minimo_acompanha_as_movimentacoes(client):
    produto = criar_produto(client)
    assert client.get(f"/produtos/{produto['id']}").json()["abaixo_do_minimo"] is True

    movimentar(client, produto["id"], "ENTRADA", 100)
    assert client.get(f"/produtos/{produto['id']}").json()["abaixo_do_minimo"] is False

    movimentar(client, produto["id"], "SAIDA", 60)
    assert client.get(f"/produtos/{produto['id']}").json()["abaixo_do_minimo"] is True
