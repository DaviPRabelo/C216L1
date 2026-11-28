import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import EstoquePage from "../../src/pages/EstoquePage.jsx";
import { listarAlmoxarifados } from "../../src/services/almoxarifados.js";
import {
  atualizarProduto,
  criarProduto,
  listarCategorias,
  listarProdutos,
  removerProduto,
} from "../../src/services/produtos.js";

vi.mock("../../src/services/almoxarifados.js", () => ({
  listarAlmoxarifados: vi.fn(),
}));

vi.mock("../../src/services/produtos.js", () => ({
  listarProdutos: vi.fn(),
  listarCategorias: vi.fn(),
  criarProduto: vi.fn(),
  atualizarProduto: vi.fn(),
  removerProduto: vi.fn(),
}));

vi.mock("../../src/context/SessaoContext.jsx", () => ({
  useSessao: () => ({
    operador: { id: 1, nome: "Davi", setor: "TI" },
    deposito: { id: 1, nome: "Central", local: "Galpao A" },
  }),
}));

const PARAFUSO = {
  id: 1,
  almoxarifado_id: 1,
  codigo: "PAR-001",
  nome: "Parafuso sextavado",
  descricao: "M8",
  categoria: "Fixadores",
  unidade: "UN",
  estoque_minimo: 50,
  saldo: 10,
  abaixo_do_minimo: true,
};

beforeEach(() => {
  vi.clearAllMocks();
  listarProdutos.mockResolvedValue([]);
  listarCategorias.mockResolvedValue([]);
  listarAlmoxarifados.mockResolvedValue([
    { id: 1, nome: "Central" },
    { id: 2, nome: "Obras" },
  ]);
});

async function preencherProduto(usuario) {
  await usuario.type(screen.getByLabelText("Código"), "LUV-001");
  await usuario.type(screen.getByLabelText("Nome"), "Luva");
  await usuario.selectOptions(screen.getByLabelText("Categoria"), "EPI");
  const minimo = screen.getByLabelText("Estoque mínimo");
  await usuario.clear(minimo);
  await usuario.type(minimo, "5");
}

describe("EstoquePage", () => {
  it("consulta apenas o depósito ativo", async () => {
    render(<EstoquePage />);

    await waitFor(() =>
      expect(listarProdutos).toHaveBeenCalledWith(expect.objectContaining({ almoxarifadoId: 1 })),
    );
    expect(listarCategorias).toHaveBeenCalledWith(1);
  });

  it("mostra o estado vazio quando não há produtos", async () => {
    render(<EstoquePage />);

    expect(
      await screen.findByText("Nenhum produto encontrado neste almoxarifado."),
    ).toBeInTheDocument();
  });

  it("lista os produtos com saldo e alerta de mínimo", async () => {
    listarProdutos.mockResolvedValue([PARAFUSO]);
    render(<EstoquePage />);

    expect(await screen.findByRole("heading", { name: "Parafuso sextavado" })).toBeInTheDocument();
    expect(screen.getByText("PAR-001")).toBeInTheDocument();
    expect(screen.getByText("Abaixo do mínimo")).toBeInTheDocument();
  });

  it("cadastra um produto no depósito ativo", async () => {
    const usuario = userEvent.setup();
    criarProduto.mockResolvedValue({ ...PARAFUSO, id: 2 });
    render(<EstoquePage />);
    await screen.findByText("Nenhum produto encontrado neste almoxarifado.");

    await usuario.click(screen.getByRole("button", { name: "Novo produto" }));
    await preencherProduto(usuario);
    await usuario.click(screen.getByRole("button", { name: "Cadastrar produto" }));

    expect(criarProduto).toHaveBeenCalledWith(
      expect.objectContaining({ codigo: "LUV-001", almoxarifado_id: 1 }),
    );
  });

  it("permite cadastrar em outro almoxarifado", async () => {
    const usuario = userEvent.setup();
    criarProduto.mockResolvedValue({ ...PARAFUSO, id: 2 });
    render(<EstoquePage />);
    await screen.findByText("Nenhum produto encontrado neste almoxarifado.");

    await usuario.click(screen.getByRole("button", { name: "Novo produto" }));
    await preencherProduto(usuario);
    await usuario.selectOptions(screen.getByLabelText("Almoxarifado"), "2");
    await usuario.click(screen.getByRole("button", { name: "Cadastrar produto" }));

    expect(criarProduto).toHaveBeenCalledWith(
      expect.objectContaining({ codigo: "LUV-001", almoxarifado_id: 2 }),
    );
  });

  it("exibe o erro de código repetido vindo do backend", async () => {
    const usuario = userEvent.setup();
    criarProduto.mockRejectedValue(new Error("Já existe um produto com o código LUV-001"));
    render(<EstoquePage />);
    await screen.findByText("Nenhum produto encontrado neste almoxarifado.");

    await usuario.click(screen.getByRole("button", { name: "Novo produto" }));
    await preencherProduto(usuario);
    await usuario.click(screen.getByRole("button", { name: "Cadastrar produto" }));

    expect(
      await screen.findByText("Já existe um produto com o código LUV-001"),
    ).toBeInTheDocument();
  });

  it("pede confirmação antes de excluir", async () => {
    const usuario = userEvent.setup();
    listarProdutos.mockResolvedValue([PARAFUSO]);
    removerProduto.mockResolvedValue(null);
    render(<EstoquePage />);
    await screen.findByRole("heading", { name: "Parafuso sextavado" });

    await usuario.click(screen.getByRole("button", { name: "Excluir Parafuso sextavado" }));
    expect(removerProduto).not.toHaveBeenCalled();

    await usuario.click(screen.getByRole("button", { name: "Confirmar exclusão" }));
    expect(removerProduto).toHaveBeenCalledWith(1);
  });

  it("mostra o erro ao excluir produto com movimentações", async () => {
    const usuario = userEvent.setup();
    listarProdutos.mockResolvedValue([PARAFUSO]);
    removerProduto.mockRejectedValue(
      new Error("Não é possível excluir um produto que já teve movimentações."),
    );
    render(<EstoquePage />);
    await screen.findByRole("heading", { name: "Parafuso sextavado" });

    await usuario.click(screen.getByRole("button", { name: "Excluir Parafuso sextavado" }));
    await usuario.click(screen.getByRole("button", { name: "Confirmar exclusão" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("movimentações");
  });

  it("abre o formulário preenchido ao editar", async () => {
    const usuario = userEvent.setup();
    listarProdutos.mockResolvedValue([PARAFUSO]);
    atualizarProduto.mockResolvedValue(PARAFUSO);
    render(<EstoquePage />);
    await screen.findByRole("heading", { name: "Parafuso sextavado" });

    await usuario.click(screen.getByRole("button", { name: "Editar Parafuso sextavado" }));

    expect(screen.getByLabelText("Código")).toHaveValue("PAR-001");
    expect(screen.getByLabelText("Estoque mínimo")).toHaveValue(50);
  });
});
