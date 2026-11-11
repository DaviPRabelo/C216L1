import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createItem, deleteItem, listItems } from "../../src/services/items.js";

const ITEM = {
  id: 1,
  nome: "Teclado",
  descricao: "Mecânico",
  categoria: "Periféricos",
  quantidade: 2,
  preco: 150,
};

function resposta({ ok = true, status = 200, corpo = {} }) {
  return { ok, status, json: async () => corpo };
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("listItems", () => {
  it("busca a lista e devolve o corpo", async () => {
    fetch.mockResolvedValue(resposta({ corpo: [ITEM] }));

    const itens = await listItems();

    expect(itens).toEqual([ITEM]);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/itens",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } }),
    );
  });
});

describe("createItem", () => {
  it("envia POST com o corpo serializado", async () => {
    fetch.mockResolvedValue(resposta({ status: 201, corpo: ITEM }));
    const dados = {
      nome: "Teclado",
      descricao: "",
      categoria: "Periféricos",
      quantidade: 1,
      preco: 10,
    };

    const criado = await createItem(dados);

    expect(criado).toEqual(ITEM);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/itens",
      expect.objectContaining({ method: "POST", body: JSON.stringify(dados) }),
    );
  });

  it("propaga a mensagem do backend em caso de conflito", async () => {
    fetch.mockResolvedValue(
      resposta({ ok: false, status: 409, corpo: { detail: "Já existe um item com esse nome" } }),
    );

    await expect(createItem({})).rejects.toThrow("Já existe um item com esse nome");
  });

  it("usa mensagem genérica quando a resposta não traz detail", async () => {
    fetch.mockResolvedValue(resposta({ ok: false, status: 500, corpo: {} }));

    await expect(createItem({})).rejects.toThrow("Erro 500");
  });
});

describe("deleteItem", () => {
  it("devolve null em um 204, sem tentar desserializar", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => {
        throw new Error("não deveria ser chamado");
      },
    });

    await expect(deleteItem(1)).resolves.toBeNull();
  });
});

describe("falha de rede", () => {
  it("traduz a rejeição do fetch em mensagem de conexão", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(listItems()).rejects.toThrow("Não foi possível conectar à API");
  });
});
