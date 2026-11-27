import { describe, expect, it } from "vitest";
import {
  ehValido,
  FOTO_MAXIMA,
  TIPOS,
  UNIDADES,
  validarFoto,
  validarLogin,
  validarMovimentacao,
  validarProduto,
} from "../../src/validation.js";

const PRODUTO = {
  codigo: "PAR-001",
  nome: "Parafuso sextavado",
  descricao: "M8",
  categoria: "Fixadores",
  unidade: "UN",
  estoque_minimo: "50",
};

const ENTRADA = { tipo: "ENTRADA", quantidade: "10", responsavel: "Davi" };
const SAIDA = { ...ENTRADA, tipo: "SAIDA", requerente: "Ana", destino: "Oficina" };

describe("validarProduto", () => {
  it("aceita um produto completo", () => {
    expect(validarProduto(PRODUTO)).toEqual({});
  });

  it("aceita descrição vazia, por ser opcional", () => {
    expect(validarProduto({ ...PRODUTO, descricao: "" })).toEqual({});
  });

  it.each([
    ["codigo", ""],
    ["codigo", "   "],
    ["codigo", "X".repeat(21)],
    ["nome", ""],
    ["nome", "N".repeat(101)],
    ["descricao", "D".repeat(201)],
    ["categoria", ""],
    ["unidade", "TONELADA"],
    ["estoque_minimo", ""],
    ["estoque_minimo", "-1"],
    ["estoque_minimo", "1.5"],
  ])("rejeita %s inválido", (campo, valor) => {
    expect(validarProduto({ ...PRODUTO, [campo]: valor })).toHaveProperty(campo);
  });

  it("acumula os erros de todos os campos", () => {
    const erros = validarProduto({
      codigo: "",
      nome: "",
      categoria: "",
      unidade: "",
      estoque_minimo: "",
    });

    expect(Object.keys(erros).sort()).toEqual([
      "categoria",
      "codigo",
      "estoque_minimo",
      "nome",
      "unidade",
    ]);
  });

  it.each(UNIDADES.map((u) => u.valor))("aceita a unidade %s", (unidade) => {
    expect(validarProduto({ ...PRODUTO, unidade })).toEqual({});
  });
});

describe("validarMovimentacao", () => {
  it("aceita entrada sem requerente nem destino", () => {
    expect(validarMovimentacao(ENTRADA)).toEqual({});
  });

  it("aceita saída com requerente e destino", () => {
    expect(validarMovimentacao(SAIDA)).toEqual({});
  });

  it("exige requerente na saída", () => {
    expect(validarMovimentacao({ ...SAIDA, requerente: "" })).toHaveProperty("requerente");
  });

  it("exige destino na saída", () => {
    expect(validarMovimentacao({ ...SAIDA, destino: "" })).toHaveProperty("destino");
  });

  it.each([
    ["quantidade", ""],
    ["quantidade", "0"],
    ["quantidade", "-5"],
    ["quantidade", "2.5"],
    ["responsavel", ""],
    ["tipo", "DEVOLUCAO"],
  ])("rejeita %s inválido", (campo, valor) => {
    expect(validarMovimentacao({ ...ENTRADA, [campo]: valor })).toHaveProperty(campo);
  });

  it.each(TIPOS.map((t) => t.valor))("aceita o tipo %s", (tipo) => {
    const dados = tipo === "SAIDA" ? SAIDA : ENTRADA;
    expect(validarMovimentacao({ ...dados, tipo })).toEqual({});
  });
});

describe("validarLogin", () => {
  it("aceita credenciais preenchidas", () => {
    expect(validarLogin({ email: "davi@almox.com", senha: "senha123" })).toEqual({});
  });

  it.each([
    ["email", ""],
    ["email", "semarroba"],
    ["senha", ""],
  ])("rejeita %s inválido", (campo, valor) => {
    const base = { email: "davi@almox.com", senha: "senha123" };
    expect(validarLogin({ ...base, [campo]: valor })).toHaveProperty(campo);
  });
});

describe("ehValido", () => {
  it("é verdadeiro sem erros", () => {
    expect(ehValido({})).toBe(true);
  });

  it("é falso com qualquer erro", () => {
    expect(ehValido({ nome: "obrigatório" })).toBe(false);
  });
});

describe("validarFoto", () => {
  const PNG = "data:image/png;base64,iVBORw0KGgo=";

  it("aceita ausência de foto", () => {
    expect(validarFoto("")).toBeNull();
    expect(validarFoto(undefined)).toBeNull();
  });

  it("aceita uma data URL de imagem", () => {
    expect(validarFoto(PNG)).toBeNull();
  });

  it("recusa arquivo que não é imagem", () => {
    expect(validarFoto("data:application/pdf;base64,AAAA")).toMatch(/imagem/);
  });

  it("recusa imagem acima do limite", () => {
    expect(validarFoto(`data:image/png;base64,${"A".repeat(FOTO_MAXIMA)}`)).toMatch(/grande/);
  });

  it("entra no resultado de validarProduto", () => {
    const erros = validarProduto({ ...PRODUTO, foto: "data:text/plain;base64,AA" });

    expect(erros).toHaveProperty("foto");
  });
});
