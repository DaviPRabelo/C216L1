import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import ItemsPage from "../../src/pages/ItemsPage.jsx";

async function cadastrar(
  usuario,
  { nome, categoria = "Periféricos", quantidade = "2", preco = "150" },
) {
  await usuario.type(screen.getByLabelText("Nome"), nome);
  await usuario.selectOptions(screen.getByLabelText("Categoria"), categoria);

  const campoQuantidade = screen.getByLabelText("Quantidade");
  await usuario.clear(campoQuantidade);
  await usuario.type(campoQuantidade, quantidade);

  await usuario.type(screen.getByLabelText("Preço"), preco);
  await usuario.click(screen.getByRole("button", { name: "Cadastrar produto" }));
}

describe("ItemsPage", () => {
  it("começa sem produtos", () => {
    render(<ItemsPage />);

    expect(screen.getByText("Nenhum produto cadastrado ainda.")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Produtos (0)" })).toBeInTheDocument();
  });

  it("mostra o produto cadastrado com categoria e preço", async () => {
    const usuario = userEvent.setup();
    render(<ItemsPage />);

    await cadastrar(usuario, { nome: "Teclado", categoria: "Periféricos", preco: "150" });

    const catalogo = screen.getByRole("list");
    expect(within(catalogo).getByRole("heading", { name: "Teclado" })).toBeInTheDocument();
    expect(within(catalogo).getByText("Periféricos")).toBeInTheDocument();
    expect(within(catalogo).getByText("R$ 150,00")).toBeInTheDocument();
    expect(screen.queryByText("Nenhum produto cadastrado ainda.")).not.toBeInTheDocument();
  });

  it("calcula o valor em estoque somando quantidade × preço", async () => {
    const usuario = userEvent.setup();
    render(<ItemsPage />);

    await cadastrar(usuario, { nome: "Teclado", quantidade: "2", preco: "150" });
    await cadastrar(usuario, { nome: "Monitor", quantidade: "3", preco: "900" });

    expect(screen.getByText("R$ 3000,00")).toBeInTheDocument();
    expect(screen.getByText(/5 unidades/)).toBeInTheDocument();
  });

  it("atualiza o contador a cada produto", async () => {
    const usuario = userEvent.setup();
    render(<ItemsPage />);

    await cadastrar(usuario, { nome: "Teclado" });
    await cadastrar(usuario, { nome: "Monitor" });

    expect(screen.getByRole("heading", { name: "Produtos (2)" })).toBeInTheDocument();
  });

  it("remove apenas o produto escolhido", async () => {
    const usuario = userEvent.setup();
    render(<ItemsPage />);
    await cadastrar(usuario, { nome: "Teclado" });
    await cadastrar(usuario, { nome: "Monitor" });

    await usuario.click(screen.getByRole("button", { name: "Remover Teclado" }));

    expect(screen.queryByRole("heading", { name: "Teclado" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Monitor" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Produtos (1)" })).toBeInTheDocument();
  });

  it("volta ao estado vazio quando tudo é removido", async () => {
    const usuario = userEvent.setup();
    render(<ItemsPage />);
    await cadastrar(usuario, { nome: "Teclado" });

    await usuario.click(screen.getByRole("button", { name: "Remover Teclado" }));

    expect(screen.getByText("Nenhum produto cadastrado ainda.")).toBeInTheDocument();
  });
});
