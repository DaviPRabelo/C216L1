import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ProdutoCard from "../../src/components/ProdutoCard.jsx";
import ProdutoForm from "../../src/components/ProdutoForm.jsx";

const PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==";

const PRODUTO = {
  id: 1,
  codigo: "PAR-001",
  nome: "Parafuso sextavado",
  descricao: "M8",
  categoria: "Fixadores",
  unidade: "UN",
  estoque_minimo: 50,
  saldo: 70,
  abaixo_do_minimo: false,
  foto: "",
};

function cartao(produto) {
  return render(
    <ul>
      <ProdutoCard produto={produto} onEditar={vi.fn()} onExcluir={vi.fn()} />
    </ul>,
  );
}

describe("ProdutoCard", () => {
  it("mostra o aviso quando o produto não tem foto", () => {
    cartao(PRODUTO);

    expect(screen.getByText("Sem foto")).toBeInTheDocument();
    expect(screen.queryByAltText(/Foto de/)).not.toBeInTheDocument();
  });

  it("exibe a foto quando existe", () => {
    cartao({ ...PRODUTO, foto: PNG });

    const imagem = screen.getByAltText("Foto de Parafuso sextavado");
    expect(imagem).toHaveAttribute("src", PNG);
    expect(screen.queryByText("Sem foto")).not.toBeInTheDocument();
  });

  it("desenha o código de barras a partir do código do produto", () => {
    cartao(PRODUTO);

    expect(screen.getByRole("img", { name: "Código de barras PAR-001" })).toBeInTheDocument();
  });

  it("esconde o botão de movimentar quando não há callback", () => {
    cartao(PRODUTO);

    expect(screen.queryByRole("button", { name: /Movimentar/ })).not.toBeInTheDocument();
  });
});

describe("ProdutoForm — foto", () => {
  it("começa sem prévia", () => {
    render(<ProdutoForm produto={null} onSalvar={vi.fn()} onCancelar={vi.fn()} />);

    expect(screen.queryByAltText("Prévia do produto")).not.toBeInTheDocument();
  });

  it("mostra a prévia depois de escolher um arquivo", async () => {
    const usuario = userEvent.setup();
    render(<ProdutoForm produto={null} onSalvar={vi.fn()} onCancelar={vi.fn()} />);

    const arquivo = new File(["conteudo-da-imagem"], "produto.png", { type: "image/png" });
    await usuario.upload(screen.getByLabelText("Foto do produto"), arquivo);

    await waitFor(() =>
      expect(screen.getByAltText("Prévia do produto")).toHaveAttribute(
        "src",
        expect.stringContaining("data:image/png;base64,"),
      ),
    );
  });

  it("permite remover a foto escolhida", async () => {
    const usuario = userEvent.setup();
    render(<ProdutoForm produto={null} onSalvar={vi.fn()} onCancelar={vi.fn()} />);

    const arquivo = new File(["x"], "produto.png", { type: "image/png" });
    await usuario.upload(screen.getByLabelText("Foto do produto"), arquivo);
    await screen.findByAltText("Prévia do produto");

    await usuario.click(screen.getByRole("button", { name: "Remover foto" }));

    expect(screen.queryByAltText("Prévia do produto")).not.toBeInTheDocument();
  });

  it("carrega a foto existente ao editar", () => {
    render(
      <ProdutoForm produto={{ ...PRODUTO, foto: PNG }} onSalvar={vi.fn()} onCancelar={vi.fn()} />,
    );

    expect(screen.getByAltText("Prévia do produto")).toHaveAttribute("src", PNG);
  });

  it("envia a foto junto com os demais campos", async () => {
    const usuario = userEvent.setup();
    const aoSalvar = vi.fn();
    render(
      <ProdutoForm produto={{ ...PRODUTO, foto: PNG }} onSalvar={aoSalvar} onCancelar={vi.fn()} />,
    );

    await usuario.click(screen.getByRole("button", { name: "Salvar alterações" }));

    expect(aoSalvar).toHaveBeenCalledWith(expect.objectContaining({ foto: PNG }));
  });
});
