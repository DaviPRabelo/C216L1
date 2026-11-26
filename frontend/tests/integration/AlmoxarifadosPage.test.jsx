import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AlmoxarifadosPage from "../../src/pages/AlmoxarifadosPage.jsx";
import {
  atualizarAlmoxarifado,
  criarAlmoxarifado,
  listarAlmoxarifados,
  removerAlmoxarifado,
} from "../../src/services/almoxarifados.js";

vi.mock("../../src/services/almoxarifados.js", () => ({
  listarAlmoxarifados: vi.fn(),
  criarAlmoxarifado: vi.fn(),
  atualizarAlmoxarifado: vi.fn(),
  removerAlmoxarifado: vi.fn(),
}));

const selecionarDeposito = vi.fn();

vi.mock("../../src/context/SessaoContext.jsx", () => ({
  useSessao: () => ({
    operador: { id: 1, nome: "Davi" },
    deposito: null,
    selecionarDeposito,
  }),
}));

const CENTRAL = {
  id: 1,
  nome: "Central",
  local: "Galpao A",
  responsavel: "Davi",
  ativo: true,
  total_produtos: 4,
  produtos_em_falta: 1,
  unidades_em_estoque: 120,
};

beforeEach(() => {
  vi.clearAllMocks();
  listarAlmoxarifados.mockResolvedValue([CENTRAL]);
});

describe("AlmoxarifadosPage", () => {
  it("mostra o resumo de estoque de cada depósito", async () => {
    render(<AlmoxarifadosPage />);

    expect(await screen.findByRole("heading", { name: "Central" })).toBeInTheDocument();
    expect(screen.getByText("Galpao A")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
  });

  it("mostra o estado vazio quando não há depósitos", async () => {
    listarAlmoxarifados.mockResolvedValue([]);
    render(<AlmoxarifadosPage />);

    expect(await screen.findByText(/Nenhum almoxarifado cadastrado/)).toBeInTheDocument();
  });

  it("seleciona o depósito e avisa quem chamou", async () => {
    const usuario = userEvent.setup();
    const aoEscolher = vi.fn();
    render(<AlmoxarifadosPage aoEscolher={aoEscolher} />);
    await screen.findByRole("heading", { name: "Central" });

    await usuario.click(screen.getByRole("button", { name: "Selecionar Central" }));

    expect(selecionarDeposito).toHaveBeenCalledWith({
      id: 1,
      nome: "Central",
      local: "Galpao A",
    });
    expect(aoEscolher).toHaveBeenCalled();
  });

  it("cadastra um depósito novo", async () => {
    const usuario = userEvent.setup();
    criarAlmoxarifado.mockResolvedValue({ ...CENTRAL, id: 2, nome: "Obras" });
    render(<AlmoxarifadosPage />);
    await screen.findByRole("heading", { name: "Central" });

    await usuario.click(screen.getByRole("button", { name: "Novo almoxarifado" }));
    await usuario.type(screen.getByLabelText("Nome"), "Obras");
    await usuario.type(screen.getByLabelText("Local"), "Patio 2");
    await usuario.click(screen.getByRole("button", { name: "Cadastrar" }));

    expect(criarAlmoxarifado).toHaveBeenCalledWith(
      expect.objectContaining({ nome: "Obras", local: "Patio 2" }),
    );
  });

  it("exige o nome antes de enviar", async () => {
    const usuario = userEvent.setup();
    render(<AlmoxarifadosPage />);
    await screen.findByRole("heading", { name: "Central" });

    await usuario.click(screen.getByRole("button", { name: "Novo almoxarifado" }));
    await usuario.click(screen.getByRole("button", { name: "Cadastrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("nome do almoxarifado");
    expect(criarAlmoxarifado).not.toHaveBeenCalled();
  });

  it("desativa sem excluir", async () => {
    const usuario = userEvent.setup();
    atualizarAlmoxarifado.mockResolvedValue({ ...CENTRAL, ativo: false });
    render(<AlmoxarifadosPage />);
    await screen.findByRole("heading", { name: "Central" });

    await usuario.click(screen.getByRole("button", { name: "Desativar" }));

    expect(atualizarAlmoxarifado).toHaveBeenCalledWith(1, { ativo: false });
  });

  it("exibe o erro ao excluir depósito com produtos", async () => {
    const usuario = userEvent.setup();
    removerAlmoxarifado.mockRejectedValue(
      new Error("Não é possível excluir um almoxarifado que ainda tem produtos cadastrados."),
    );
    render(<AlmoxarifadosPage />);
    await screen.findByRole("heading", { name: "Central" });

    await usuario.click(screen.getByRole("button", { name: "Excluir Central" }));
    await usuario.click(screen.getByRole("button", { name: "Confirmar exclusão" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("produtos cadastrados");
  });
});
