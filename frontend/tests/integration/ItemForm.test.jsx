import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ItemForm from "../../src/components/ItemForm.jsx";

const BOTAO = { name: "Cadastrar produto" };

async function preencher(usuario, campos = {}) {
  const {
    nome = "Teclado",
    categoria = "Periféricos",
    quantidade = "2",
    preco = "150",
    descricao = "",
  } = campos;

  if (nome) await usuario.type(screen.getByLabelText("Nome"), nome);
  if (categoria) await usuario.selectOptions(screen.getByLabelText("Categoria"), categoria);

  const campoQuantidade = screen.getByLabelText("Quantidade");
  await usuario.clear(campoQuantidade);
  if (quantidade) await usuario.type(campoQuantidade, quantidade);

  if (preco) await usuario.type(screen.getByLabelText("Preço"), preco);
  if (descricao) await usuario.type(screen.getByLabelText("Descrição"), descricao);
}

describe("ItemForm", () => {
  it("envia os dados preenchidos, convertendo números", async () => {
    const usuario = userEvent.setup();
    const aoAdicionar = vi.fn();
    render(<ItemForm onAdicionar={aoAdicionar} />);

    await preencher(usuario, { descricao: "Mecânico" });
    await usuario.click(screen.getByRole("button", BOTAO));

    expect(aoAdicionar).toHaveBeenCalledWith({
      nome: "Teclado",
      descricao: "Mecânico",
      categoria: "Periféricos",
      quantidade: 2,
      preco: 150,
    });
  });

  it("bloqueia o envio e lista os erros quando o formulário está vazio", async () => {
    const usuario = userEvent.setup();
    const aoAdicionar = vi.fn();
    render(<ItemForm onAdicionar={aoAdicionar} />);

    await usuario.click(screen.getByRole("button", BOTAO));

    const alertas = screen.getAllByRole("alert").map((elemento) => elemento.textContent);
    expect(alertas).toContain("O nome é obrigatório");
    expect(alertas).toContain("Escolha uma categoria");
    expect(alertas).toContain("O preço é obrigatório");
    expect(aoAdicionar).not.toHaveBeenCalled();
  });

  it("rejeita quantidade zero", async () => {
    const usuario = userEvent.setup();
    const aoAdicionar = vi.fn();
    render(<ItemForm onAdicionar={aoAdicionar} />);

    await preencher(usuario, { quantidade: "0" });
    await usuario.click(screen.getByRole("button", BOTAO));

    expect(screen.getByText("A quantidade deve ser pelo menos 1")).toBeInTheDocument();
    expect(aoAdicionar).not.toHaveBeenCalled();
  });

  it("limpa os campos após um envio válido", async () => {
    const usuario = userEvent.setup();
    render(<ItemForm onAdicionar={vi.fn()} />);

    await preencher(usuario);
    await usuario.click(screen.getByRole("button", BOTAO));

    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(screen.getByLabelText("Categoria")).toHaveValue("");
    expect(screen.getByLabelText("Quantidade")).toHaveValue(1);
  });

  it("remove espaços das bordas do nome antes de enviar", async () => {
    const usuario = userEvent.setup();
    const aoAdicionar = vi.fn();
    render(<ItemForm onAdicionar={aoAdicionar} />);

    await preencher(usuario, { nome: "  Teclado  " });
    await usuario.click(screen.getByRole("button", BOTAO));

    expect(aoAdicionar).toHaveBeenCalledWith(expect.objectContaining({ nome: "Teclado" }));
  });

  it("some com os erros depois que o formulário é corrigido", async () => {
    const usuario = userEvent.setup();
    render(<ItemForm onAdicionar={vi.fn()} />);
    const botao = screen.getByRole("button", BOTAO);

    await usuario.click(botao);
    expect(screen.getAllByRole("alert").length).toBeGreaterThan(0);

    await preencher(usuario);
    await usuario.click(botao);

    expect(screen.queryAllByRole("alert")).toHaveLength(0);
  });
  it("mantém os valores digitados quando o envio falha", async () => {
    const usuario = userEvent.setup();
    const aoAdicionar = vi.fn().mockRejectedValue(new Error("Já existe um item com esse nome"));
    render(<ItemForm onAdicionar={aoAdicionar} />);

    await preencher(usuario);
    await usuario.click(screen.getByRole("button", BOTAO));

    expect(screen.getByLabelText("Nome")).toHaveValue("Teclado");
  });
});
