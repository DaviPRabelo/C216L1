import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import MovimentacoesPage from "../../src/pages/MovimentacoesPage.jsx";
import { listarMovimentacoes, registrarMovimentacao } from "../../src/services/movimentacoes.js";
import { listarProdutos } from "../../src/services/produtos.js";

vi.mock("../../src/services/produtos.js", () => ({ listarProdutos: vi.fn() }));
vi.mock("../../src/services/movimentacoes.js", () => ({
  listarMovimentacoes: vi.fn(),
  registrarMovimentacao: vi.fn(),
}));
vi.mock("../../src/context/SessaoContext.jsx", () => ({
  useSessao: () => ({
    operador: { id: 1, nome: "Davi", setor: "TI" },
    deposito: { id: 1, nome: "Central" },
  }),
}));

const PARAFUSO = {
  id: 1,
  codigo: "PAR-001",
  nome: "Parafuso sextavado",
  unidade: "UN",
  saldo: 70,
  estoque_minimo: 50,
  abaixo_do_minimo: false,
};

beforeEach(() => {
  vi.clearAllMocks();
  listarProdutos.mockResolvedValue([PARAFUSO]);
  listarMovimentacoes.mockResolvedValue([]);
});

async function escolherProduto(usuario) {
  await usuario.click(await screen.findByRole("button", { name: "Movimentar Parafuso sextavado" }));
}

async function preencherQuantidade(usuario, valor) {
  const campo = screen.getByLabelText("Quantidade");
  await usuario.clear(campo);
  await usuario.type(campo, valor);
}

describe("MovimentacoesPage", () => {
  it("lista os produtos do depósito ativo", async () => {
    render(<MovimentacoesPage />);

    expect(await screen.findByText("Parafuso sextavado")).toBeInTheDocument();
    expect(listarProdutos).toHaveBeenCalledWith({ almoxarifadoId: 1 });
  });

  it("só mostra o formulário depois de escolher o produto", async () => {
    const usuario = userEvent.setup();
    render(<MovimentacoesPage />);

    expect(screen.queryByLabelText("Quantidade")).not.toBeInTheDocument();

    await escolherProduto(usuario);

    expect(screen.getByLabelText("Quantidade")).toBeInTheDocument();
    expect(listarMovimentacoes).toHaveBeenCalledWith(1);
  });

  it("preenche o responsável com o operador logado", async () => {
    const usuario = userEvent.setup();
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);

    expect(screen.getByLabelText("Responsável")).toHaveValue("Davi");
  });

  it("registra uma entrada", async () => {
    const usuario = userEvent.setup();
    registrarMovimentacao.mockResolvedValue({ id: 1 });
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);
    await preencherQuantidade(usuario, "100");
    await usuario.click(screen.getByRole("button", { name: "Registrar movimentação" }));

    expect(registrarMovimentacao).toHaveBeenCalledWith(
      1,
      expect.objectContaining({ tipo: "ENTRADA", quantidade: 100, responsavel: "Davi" }),
    );
  });

  it("esconde requerente e destino na entrada", async () => {
    const usuario = userEvent.setup();
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);

    expect(screen.queryByLabelText("Requerente")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Destino")).not.toBeInTheDocument();
  });

  it("exige requerente e destino ao escolher saída", async () => {
    const usuario = userEvent.setup();
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "SAIDA");
    await preencherQuantidade(usuario, "10");
    await usuario.click(screen.getByRole("button", { name: "Registrar movimentação" }));

    const alertas = screen.getAllByRole("alert").map((e) => e.textContent);
    expect(alertas).toContain("Toda saída precisa do requerente");
    expect(alertas).toContain("Toda saída precisa do destino");
    expect(registrarMovimentacao).not.toHaveBeenCalled();
  });

  it("registra uma saída completa", async () => {
    const usuario = userEvent.setup();
    registrarMovimentacao.mockResolvedValue({ id: 2 });
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "SAIDA");
    await preencherQuantidade(usuario, "30");
    await usuario.type(screen.getByLabelText("Requerente"), "Ana");
    await usuario.type(screen.getByLabelText("Destino"), "Oficina");
    await usuario.click(screen.getByRole("button", { name: "Registrar movimentação" }));

    expect(registrarMovimentacao).toHaveBeenCalledWith(
      1,
      expect.objectContaining({ tipo: "SAIDA", requerente: "Ana", destino: "Oficina" }),
    );
  });

  it("exibe a mensagem de saldo insuficiente vinda do backend", async () => {
    const usuario = userEvent.setup();
    registrarMovimentacao.mockRejectedValue(
      new Error("Saldo insuficiente: disponível 70 UN, solicitado 500 UN"),
    );
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "SAIDA");
    await preencherQuantidade(usuario, "500");
    await usuario.type(screen.getByLabelText("Requerente"), "Ana");
    await usuario.type(screen.getByLabelText("Destino"), "Oficina");
    await usuario.click(screen.getByRole("button", { name: "Registrar movimentação" }));

    expect(await screen.findByText(/Saldo insuficiente/)).toBeInTheDocument();
  });

  it("mostra o histórico do produto escolhido", async () => {
    const usuario = userEvent.setup();
    listarMovimentacoes.mockResolvedValue([
      {
        id: 2,
        tipo: "SAIDA",
        quantidade: 30,
        responsavel: "Davi",
        requerente: "Ana",
        destino: "Oficina",
        observacao: "requisicao 12",
        criada_em: "2026-11-26T10:00:00Z",
      },
    ]);
    render(<MovimentacoesPage />);

    await escolherProduto(usuario);

    expect(await screen.findByText("Saída de 30")).toBeInTheDocument();
    expect(screen.getByText("requisicao 12")).toBeInTheDocument();
  });
});
