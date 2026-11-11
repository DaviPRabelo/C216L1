import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ItemsPage from "../../src/pages/ItemsPage.jsx";
import { createItem, deleteItem, listItems } from "../../src/services/items.js";

vi.mock("../../src/services/items.js", () => ({
  listItems: vi.fn(),
  createItem: vi.fn(),
  deleteItem: vi.fn(),
}));

const TECLADO = {
  id: 1,
  nome: "Teclado",
  descricao: "Mecânico",
  categoria: "Periféricos",
  quantidade: 2,
  preco: 150,
};

async function preencherFormulario(usuario, nome = "Monitor") {
  await usuario.type(screen.getByLabelText("Nome"), nome);
  await usuario.selectOptions(screen.getByLabelText("Categoria"), "Eletrônicos");
  const quantidade = screen.getByLabelText("Quantidade");
  await usuario.clear(quantidade);
  await usuario.type(quantidade, "3");
  await usuario.type(screen.getByLabelText("Preço"), "900");
  await usuario.click(screen.getByRole("button", { name: "Cadastrar produto" }));
}

beforeEach(() => {
  vi.clearAllMocks();
  listItems.mockResolvedValue([]);
});

describe("ItemsPage — carregamento", () => {
  it("exibe o estado de carregando antes da resposta", () => {
    listItems.mockReturnValue(new Promise(() => {}));
    render(<ItemsPage />);

    expect(screen.getByText("Carregando produtos...")).toBeInTheDocument();
  });

  it("mostra os produtos vindos da API", async () => {
    listItems.mockResolvedValue([TECLADO]);
    render(<ItemsPage />);

    expect(await screen.findByRole("heading", { name: "Teclado" })).toBeInTheDocument();
    const catalogo = screen.getByRole("list");
    expect(within(catalogo).getByText("Periféricos")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Produtos (1)" })).toBeInTheDocument();
  });

  it("mostra o catálogo vazio quando a API não devolve nada", async () => {
    render(<ItemsPage />);

    expect(await screen.findByText("Nenhum produto cadastrado ainda.")).toBeInTheDocument();
  });

  it("exibe a mensagem quando a API está fora do ar", async () => {
    listItems.mockRejectedValue(new Error("Não foi possível conectar à API"));
    render(<ItemsPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível conectar à API");
  });
});

describe("ItemsPage — cadastro", () => {
  it("envia o produto para a API e exibe na lista", async () => {
    const usuario = userEvent.setup();
    const criado = {
      ...TECLADO,
      id: 2,
      nome: "Monitor",
      categoria: "Eletrônicos",
      quantidade: 3,
      preco: 900,
    };
    createItem.mockResolvedValue(criado);
    render(<ItemsPage />);
    await screen.findByText("Nenhum produto cadastrado ainda.");

    await preencherFormulario(usuario);

    expect(createItem).toHaveBeenCalledWith({
      nome: "Monitor",
      descricao: "",
      categoria: "Eletrônicos",
      quantidade: 3,
      preco: 900,
    });
    expect(await screen.findByRole("heading", { name: "Monitor" })).toBeInTheDocument();
  });

  it("mostra o erro de nome repetido e preserva o que foi digitado", async () => {
    const usuario = userEvent.setup();
    createItem.mockRejectedValue(new Error("Já existe um item com esse nome"));
    render(<ItemsPage />);
    await screen.findByText("Nenhum produto cadastrado ainda.");

    await preencherFormulario(usuario, "Teclado");

    expect(await screen.findByRole("alert")).toHaveTextContent("Já existe um item com esse nome");
    expect(screen.getByLabelText("Nome")).toHaveValue("Teclado");
  });
});

describe("ItemsPage — remoção", () => {
  it("chama a API e tira o produto da lista", async () => {
    const usuario = userEvent.setup();
    listItems.mockResolvedValue([TECLADO]);
    deleteItem.mockResolvedValue(null);
    render(<ItemsPage />);
    await screen.findByRole("heading", { name: "Teclado" });

    await usuario.click(screen.getByRole("button", { name: "Remover Teclado" }));

    expect(deleteItem).toHaveBeenCalledWith(1);
    await waitFor(() =>
      expect(screen.getByText("Nenhum produto cadastrado ainda.")).toBeInTheDocument(),
    );
  });

  it("exibe a mensagem quando a remoção falha", async () => {
    const usuario = userEvent.setup();
    listItems.mockResolvedValue([TECLADO]);
    deleteItem.mockRejectedValue(new Error("Erro 500 ao falar com a API"));
    render(<ItemsPage />);
    await screen.findByRole("heading", { name: "Teclado" });

    await usuario.click(screen.getByRole("button", { name: "Remover Teclado" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Erro 500");
  });
});
