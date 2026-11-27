import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import InventarioPage from "../../src/pages/InventarioPage.jsx";
import {
  abrirInventario,
  contarItem,
  fecharInventario,
  listarInventarios,
  obterInventario,
} from "../../src/services/inventarios.js";

vi.mock("../../src/services/inventarios.js", () => ({
  listarInventarios: vi.fn(),
  obterInventario: vi.fn(),
  abrirInventario: vi.fn(),
  contarItem: vi.fn(),
  fecharInventario: vi.fn(),
}));

vi.mock("../../src/context/SessaoContext.jsx", () => ({
  useSessao: () => ({
    operador: { id: 1, nome: "Davi", setor: "TI" },
    deposito: { id: 1, nome: "Central" },
  }),
}));

function item(extras = {}) {
  return {
    id: 1,
    produto_id: 10,
    produto_codigo: "PAR-001",
    produto_nome: "Parafuso sextavado",
    unidade: "UN",
    saldo_sistema: 100,
    quantidade_contada: null,
    divergencia: null,
    ...extras,
  };
}

function inventario(extras = {}) {
  const itens = extras.itens ?? [item()];
  return {
    id: 7,
    almoxarifado_id: 1,
    data: "2026-11-27",
    responsavel: "Davi",
    status: "ABERTO",
    criado_em: "2026-11-27T10:00:00Z",
    itens,
    itens_contados: itens.filter((i) => i.quantidade_contada !== null).length,
    itens_divergentes: itens.filter((i) => ![null, 0].includes(i.divergencia)).length,
    ...extras,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  listarInventarios.mockResolvedValue([]);
});

describe("InventarioPage — abertura", () => {
  it("oferece abrir uma contagem quando não há inventário aberto", async () => {
    render(<InventarioPage />);

    expect(await screen.findByRole("button", { name: "Abrir inventário" })).toBeInTheDocument();
    expect(screen.getByText(/Nenhuma contagem registrada/)).toBeInTheDocument();
  });

  it("preenche o responsável com o operador logado", async () => {
    render(<InventarioPage />);

    expect(await screen.findByLabelText("Responsável pela contagem")).toHaveValue("Davi");
  });

  it("exige o responsável antes de chamar a API", async () => {
    const usuario = userEvent.setup();
    render(<InventarioPage />);
    await usuario.clear(await screen.findByLabelText("Responsável pela contagem"));

    await usuario.click(screen.getByRole("button", { name: "Abrir inventário" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("quem está fazendo");
    expect(abrirInventario).not.toHaveBeenCalled();
  });

  it("abre a contagem e mostra a tabela com o saldo congelado", async () => {
    const usuario = userEvent.setup();
    abrirInventario.mockResolvedValue(inventario());
    render(<InventarioPage />);
    await screen.findByRole("button", { name: "Abrir inventário" });

    await usuario.click(screen.getByRole("button", { name: "Abrir inventário" }));

    expect(abrirInventario).toHaveBeenCalledWith({ almoxarifado_id: 1, responsavel: "Davi" });
    expect(await screen.findByText("Parafuso sextavado")).toBeInTheDocument();
    expect(screen.getByText("100 UN")).toBeInTheDocument();
  });

  it("exibe o erro de inventário já aberto", async () => {
    const usuario = userEvent.setup();
    abrirInventario.mockRejectedValue(new Error("Já existe um inventário aberto"));
    render(<InventarioPage />);
    await screen.findByRole("button", { name: "Abrir inventário" });

    await usuario.click(screen.getByRole("button", { name: "Abrir inventário" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Já existe um inventário aberto");
  });
});

describe("InventarioPage — contagem", () => {
  function comInventarioAberto(itens) {
    const inv = inventario(itens ? { itens } : {});
    listarInventarios.mockResolvedValue([inv]);
    obterInventario.mockResolvedValue(inv);
    return inv;
  }

  it("carrega o inventário aberto do depósito", async () => {
    comInventarioAberto();
    render(<InventarioPage />);

    expect(await screen.findByText("Contagem de 27/11/2026")).toBeInTheDocument();
    expect(listarInventarios).toHaveBeenCalledWith(1);
    expect(obterInventario).toHaveBeenCalledWith(7);
  });

  it("avisa quantos itens faltam contar", async () => {
    comInventarioAberto();
    render(<InventarioPage />);

    expect(await screen.findByText("Faltam 1 itens para poder fechar.")).toBeInTheDocument();
  });

  it("envia a contagem ao sair do campo", async () => {
    const usuario = userEvent.setup();
    comInventarioAberto();
    contarItem.mockResolvedValue(
      inventario({ itens: [item({ quantidade_contada: 93, divergencia: -7 })] }),
    );
    render(<InventarioPage />);
    const campo = await screen.findByLabelText("Contagem de Parafuso sextavado");

    await usuario.type(campo, "93");
    await usuario.tab();

    await waitFor(() => expect(contarItem).toHaveBeenCalledWith(7, 10, 93));
  });

  it("mostra a falta em destaque", async () => {
    comInventarioAberto([item({ quantidade_contada: 93, divergencia: -7 })]);
    render(<InventarioPage />);

    expect(await screen.findByText("-7")).toBeInTheDocument();
  });

  it("mostra a sobra com sinal de mais", async () => {
    comInventarioAberto([item({ quantidade_contada: 105, divergencia: 5 })]);
    render(<InventarioPage />);

    expect(await screen.findByText("+5")).toBeInTheDocument();
  });

  it("marca como conferido quando não há divergência", async () => {
    comInventarioAberto([item({ quantidade_contada: 100, divergencia: 0 })]);
    render(<InventarioPage />);

    expect(await screen.findByText("confere")).toBeInTheDocument();
  });

  it("não envia nada quando o campo fica vazio", async () => {
    const usuario = userEvent.setup();
    comInventarioAberto();
    render(<InventarioPage />);
    const campo = await screen.findByLabelText("Contagem de Parafuso sextavado");

    await usuario.click(campo);
    await usuario.tab();

    expect(contarItem).not.toHaveBeenCalled();
  });

  it("fecha o inventário", async () => {
    const usuario = userEvent.setup();
    comInventarioAberto([item({ quantidade_contada: 100, divergencia: 0 })]);
    fecharInventario.mockResolvedValue(inventario({ status: "FECHADO" }));
    render(<InventarioPage />);
    await screen.findByText("Contagem de 27/11/2026");

    await usuario.click(screen.getByRole("button", { name: "Fechar inventário" }));

    expect(fecharInventario).toHaveBeenCalledWith(7);
  });

  it("exibe o erro de contagem incompleta ao tentar fechar", async () => {
    const usuario = userEvent.setup();
    comInventarioAberto();
    fecharInventario.mockRejectedValue(new Error("Ainda faltam 1 itens para contar"));
    render(<InventarioPage />);
    await screen.findByText("Contagem de 27/11/2026");

    await usuario.click(screen.getByRole("button", { name: "Fechar inventário" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Ainda faltam 1 itens");
  });

  it("lista as contagens anteriores com o status", async () => {
    listarInventarios.mockResolvedValue([
      inventario({ id: 3, status: "FECHADO", itens: [], itens_divergentes: 2 }),
    ]);
    render(<InventarioPage />);

    expect(await screen.findByText("Fechado")).toBeInTheDocument();
    expect(screen.getByText("2 divergências")).toBeInTheDocument();
  });
});
