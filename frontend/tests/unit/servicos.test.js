import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { listarAlmoxarifados } from "../../src/services/almoxarifados.js";
import { entrar } from "../../src/services/auth.js";
import { registrarMovimentacao } from "../../src/services/movimentacoes.js";
import {
  criarProduto,
  listarCategorias,
  listarProdutos,
  removerProduto,
} from "../../src/services/produtos.js";

const API = "http://localhost:8000";

function resposta({ ok = true, status = 200, corpo = {} } = {}) {
  return { ok, status, json: async () => corpo };
}

function urlChamada() {
  return fetch.mock.calls[0][0];
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(resposta({ corpo: [] })));
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("montagem da URL", () => {
  it("lista produtos sem filtro", async () => {
    await listarProdutos();

    expect(urlChamada()).toBe(`${API}/produtos`);
  });

  it("inclui o almoxarifado na consulta", async () => {
    await listarProdutos({ almoxarifadoId: 3 });

    expect(urlChamada()).toBe(`${API}/produtos?almoxarifado_id=3`);
  });

  it("combina almoxarifado, categoria e filtro de mínimo", async () => {
    await listarProdutos({ almoxarifadoId: 1, categoria: "EPI", abaixoDoMinimo: true });

    const url = urlChamada();
    expect(url).toContain("almoxarifado_id=1");
    expect(url).toContain("categoria=EPI");
    expect(url).toContain("abaixo_do_minimo=true");
  });

  it("escapa acentos e espaços na categoria", async () => {
    await listarProdutos({ categoria: "Material elétrico" });

    expect(urlChamada()).toContain("categoria=Material+el%C3%A9trico");
  });

  it("filtra categorias pelo almoxarifado", async () => {
    await listarCategorias(7);

    expect(urlChamada()).toBe(`${API}/produtos/categorias?almoxarifado_id=7`);
  });

  it("pede só os almoxarifados ativos quando solicitado", async () => {
    await listarAlmoxarifados({ apenasAtivos: true });

    expect(urlChamada()).toBe(`${API}/almoxarifados?apenas_ativos=true`);
  });

  it("aninha a movimentação sob o produto", async () => {
    fetch.mockResolvedValue(resposta({ status: 201, corpo: { id: 1 } }));
    await registrarMovimentacao(5, { tipo: "ENTRADA", quantidade: 10 });

    expect(urlChamada()).toBe(`${API}/produtos/5/movimentacoes`);
  });
});

describe("envio do corpo", () => {
  it("serializa o produto em JSON", async () => {
    fetch.mockResolvedValue(resposta({ status: 201, corpo: { id: 1 } }));
    const dados = { codigo: "PAR-001", nome: "Parafuso" };

    await criarProduto(dados);

    const opcoes = fetch.mock.calls[0][1];
    expect(opcoes.method).toBe("POST");
    expect(opcoes.body).toBe(JSON.stringify(dados));
    expect(opcoes.headers).toEqual({ "Content-Type": "application/json" });
  });

  it("envia DELETE sem corpo", async () => {
    fetch.mockResolvedValue({ ok: true, status: 204, json: async () => null });

    await expect(removerProduto(1)).resolves.toBeNull();
    expect(fetch.mock.calls[0][1].method).toBe("DELETE");
  });
});

describe("tratamento de erro", () => {
  it("propaga a mensagem do backend", async () => {
    fetch.mockResolvedValue(
      resposta({ ok: false, status: 409, corpo: { detail: "Saldo insuficiente" } }),
    );

    await expect(registrarMovimentacao(1, {})).rejects.toThrow("Saldo insuficiente");
  });

  it("usa mensagem genérica quando não há detail", async () => {
    fetch.mockResolvedValue(resposta({ ok: false, status: 500, corpo: {} }));

    await expect(listarProdutos()).rejects.toThrow("Erro 500");
  });

  it("traduz a rejeição do fetch em falha de conexão", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(entrar("davi@almox.com", "senha123")).rejects.toThrow(
      /não foi possível|conectar/i,
    );
  });

  it("não tenta desserializar um 204", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => {
        throw new Error("não deveria ser chamado");
      },
    });

    await expect(removerProduto(1)).resolves.toBeNull();
  });
});
