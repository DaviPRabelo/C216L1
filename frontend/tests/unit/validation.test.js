import { describe, expect, it } from "vitest";
import {
  CATEGORIAS,
  DESCRICAO_MAXIMA,
  ehValido,
  formatarMoeda,
  NOME_MAXIMO,
  PRECO_MAXIMO,
  QUANTIDADE_MAXIMA,
  validarCategoria,
  validarDescricao,
  validarItem,
  validarNome,
  validarPreco,
  validarQuantidade,
} from "../../src/validation.js";

const ITEM_VALIDO = {
  nome: "Teclado",
  descricao: "Mecânico",
  categoria: "Periféricos",
  quantidade: 2,
  preco: 150,
};

describe("validarNome", () => {
  it("aceita um nome válido", () => {
    expect(validarNome("Teclado")).toBeNull();
  });

  it("remove espaços das bordas antes de validar", () => {
    expect(validarNome("  Teclado  ")).toBeNull();
  });

  it.each([
    ["string vazia", ""],
    ["apenas espaços", "   "],
    ["undefined", undefined],
    ["null", null],
  ])("rejeita nome com %s", (_rotulo, entrada) => {
    expect(validarNome(entrada)).toBe("O nome é obrigatório");
  });

  it("rejeita nome acima do limite", () => {
    expect(validarNome("a".repeat(NOME_MAXIMO + 1))).toMatch(/até 60 caracteres/);
  });

  it("aceita nome exatamente no limite", () => {
    expect(validarNome("a".repeat(NOME_MAXIMO))).toBeNull();
  });
});

describe("validarDescricao", () => {
  it("aceita descrição vazia, por ser opcional", () => {
    expect(validarDescricao("")).toBeNull();
  });

  it("rejeita descrição acima do limite", () => {
    expect(validarDescricao("a".repeat(DESCRICAO_MAXIMA + 1))).toMatch(/até 200 caracteres/);
  });
});

describe("validarCategoria", () => {
  it.each(CATEGORIAS)("aceita a categoria %s", (categoria) => {
    expect(validarCategoria(categoria)).toBeNull();
  });

  it("exige que uma categoria seja escolhida", () => {
    expect(validarCategoria("")).toBe("Escolha uma categoria");
  });

  it("rejeita categoria fora da lista", () => {
    expect(validarCategoria("Automóveis")).toBe("Categoria inválida");
  });
});

describe("validarQuantidade", () => {
  it("aceita quantidade inteira positiva", () => {
    expect(validarQuantidade(3)).toBeNull();
  });

  it("aceita string numérica vinda do input", () => {
    expect(validarQuantidade("3")).toBeNull();
  });

  it.each([
    ["zero", 0, "A quantidade deve ser pelo menos 1"],
    ["negativa", -1, "A quantidade deve ser pelo menos 1"],
    ["fracionária", 1.5, "A quantidade deve ser um número inteiro"],
    ["vazia", "", "A quantidade é obrigatória"],
  ])("rejeita quantidade %s", (_rotulo, entrada, esperado) => {
    expect(validarQuantidade(entrada)).toBe(esperado);
  });

  it("rejeita quantidade acima do limite", () => {
    expect(validarQuantidade(QUANTIDADE_MAXIMA + 1)).toMatch(/não pode passar/);
  });
});

describe("validarPreco", () => {
  it("aceita preço positivo", () => {
    expect(validarPreco(150.5)).toBeNull();
  });

  it("aceita preço zero", () => {
    expect(validarPreco(0)).toBeNull();
  });

  it.each([
    ["vazio", "", "O preço é obrigatório"],
    ["não numérico", "abc", "O preço deve ser um número"],
    ["negativo", -1, "O preço não pode ser negativo"],
  ])("rejeita preço %s", (_rotulo, entrada, esperado) => {
    expect(validarPreco(entrada)).toBe(esperado);
  });

  it("rejeita preço acima do limite", () => {
    expect(validarPreco(PRECO_MAXIMO + 1)).toMatch(/não pode passar/);
  });
});

describe("validarItem", () => {
  it("devolve objeto vazio quando tudo é válido", () => {
    expect(validarItem(ITEM_VALIDO)).toEqual({});
  });

  it("acumula os erros de todos os campos inválidos", () => {
    const erros = validarItem({ nome: "", descricao: "", categoria: "", quantidade: 0, preco: -1 });

    expect(Object.keys(erros).sort()).toEqual(["categoria", "nome", "preco", "quantidade"]);
  });

  it("não reclama da descrição quando ela está vazia", () => {
    const erros = validarItem({ ...ITEM_VALIDO, descricao: "" });

    expect(erros.descricao).toBeUndefined();
  });
});

describe("ehValido", () => {
  it("é verdadeiro sem erros", () => {
    expect(ehValido({})).toBe(true);
  });

  it("é falso com qualquer erro", () => {
    expect(ehValido({ nome: "O nome é obrigatório" })).toBe(false);
  });
});

describe("formatarMoeda", () => {
  it.each([
    [150, "R$ 150,00"],
    [0, "R$ 0,00"],
    [1234.5, "R$ 1234,50"],
    [99.999, "R$ 100,00"],
  ])("formata %s como %s", (entrada, esperado) => {
    expect(formatarMoeda(entrada)).toBe(esperado);
  });
});
