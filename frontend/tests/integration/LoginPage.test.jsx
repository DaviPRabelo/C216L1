import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProvedorDeSessao } from "../../src/context/SessaoContext.jsx";
import LoginPage from "../../src/pages/LoginPage.jsx";
import { cadastrar, entrar } from "../../src/services/auth.js";

vi.mock("../../src/services/auth.js", () => ({
  entrar: vi.fn(),
  cadastrar: vi.fn(),
}));

const OPERADOR = { id: 1, nome: "Davi", email: "davi@almox.com", setor: "TI" };

function montar() {
  return render(
    <ProvedorDeSessao>
      <LoginPage />
    </ProvedorDeSessao>,
  );
}

async function preencher(usuario, email = "davi@almox.com", senha = "senha123") {
  if (email) await usuario.type(screen.getByLabelText("E-mail"), email);
  if (senha) await usuario.type(screen.getByLabelText("Senha"), senha);
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("LoginPage", () => {
  it("mostra o formulário de entrada por padrão", () => {
    montar();

    expect(screen.getByRole("button", { name: "Entrar" })).toBeInTheDocument();
    expect(screen.queryByLabelText("Nome")).not.toBeInTheDocument();
  });

  it("autentica com as credenciais informadas", async () => {
    const usuario = userEvent.setup();
    entrar.mockResolvedValue(OPERADOR);
    montar();

    await preencher(usuario);
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));

    expect(entrar).toHaveBeenCalledWith("davi@almox.com", "senha123");
  });

  it("exige e-mail e senha antes de chamar a API", async () => {
    const usuario = userEvent.setup();
    montar();

    await usuario.click(screen.getByRole("button", { name: "Entrar" }));

    const alertas = screen.getAllByRole("alert").map((e) => e.textContent);
    expect(alertas).toContain("O e-mail é obrigatório");
    expect(alertas).toContain("A senha é obrigatória");
    expect(entrar).not.toHaveBeenCalled();
  });

  it("recusa e-mail sem arroba", async () => {
    const usuario = userEvent.setup();
    montar();

    await preencher(usuario, "semarroba");
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));

    expect(screen.getByText("Informe um e-mail válido")).toBeInTheDocument();
    expect(entrar).not.toHaveBeenCalled();
  });

  it("exibe a mensagem do backend quando a senha está errada", async () => {
    const usuario = userEvent.setup();
    entrar.mockRejectedValue(new Error("E-mail ou senha incorretos"));
    montar();

    await preencher(usuario);
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("E-mail ou senha incorretos")).toBeInTheDocument();
  });

  it("alterna para o cadastro e mostra os campos extras", async () => {
    const usuario = userEvent.setup();
    montar();

    await usuario.click(screen.getByRole("button", { name: /criar agora/i }));

    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("Setor")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Criar acesso" })).toBeInTheDocument();
  });

  it("cadastra um operador novo", async () => {
    const usuario = userEvent.setup();
    cadastrar.mockResolvedValue(OPERADOR);
    montar();

    await usuario.click(screen.getByRole("button", { name: /criar agora/i }));
    await usuario.type(screen.getByLabelText("Nome"), "Davi");
    await usuario.type(screen.getByLabelText("Setor"), "TI");
    await preencher(usuario);
    await usuario.click(screen.getByRole("button", { name: "Criar acesso" }));

    expect(cadastrar).toHaveBeenCalledWith({
      nome: "Davi",
      setor: "TI",
      email: "davi@almox.com",
      senha: "senha123",
    });
  });
});
