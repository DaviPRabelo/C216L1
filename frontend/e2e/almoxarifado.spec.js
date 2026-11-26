import { expect, test } from "@playwright/test";

const API = process.env.E2E_API_URL ?? "http://localhost:8000";

// Cada teste trabalha com nomes próprios: o banco é compartilhado e os testes
// rodam em paralelo, então a limpeza precisa alcançar só o que o teste criou.
let sufixo;

const nomeDeposito = () => `E2E Deposito ${sufixo}`;
const codigoProduto = () => `E2E-${sufixo}`;

test.beforeEach(async ({ page }, info) => {
  sufixo = `w${info.workerIndex}-${Date.now()}`;

  await page.goto("/");
  await page.getByRole("button", { name: /criar agora/i }).click();
  await page.getByLabel("Nome").fill(`Operador ${sufixo}`);
  await page.getByLabel("Setor").fill("TI");
  await page.getByLabel("E-mail").fill(`e2e-${sufixo}@almox.com`);
  await page.getByLabel("Senha").fill("senha123");
  await page.getByRole("button", { name: "Criar acesso" }).click();

  await expect(page.getByRole("button", { name: "Sair" })).toBeVisible();
});

test.afterEach(async ({ request }) => {
  const produtos = await (await request.get(`${API}/produtos`)).json();
  for (const produto of produtos.filter((p) => p.codigo.startsWith("E2E-"))) {
    await request.delete(`${API}/produtos/${produto.id}`);
  }
  const depositos = await (await request.get(`${API}/almoxarifados`)).json();
  for (const deposito of depositos.filter((d) => d.nome.startsWith("E2E Deposito"))) {
    await request.delete(`${API}/almoxarifados/${deposito.id}`);
  }
});

async function criarEEntrarNoDeposito(page) {
  await page.getByRole("button", { name: "Almoxarifados", exact: true }).click();
  await page.getByRole("button", { name: "Novo almoxarifado" }).click();
  await page.getByLabel("Nome").fill(nomeDeposito());
  await page.getByLabel("Local").fill("Galpao E2E");
  await page.getByRole("button", { name: "Cadastrar" }).click();

  await page.getByRole("button", { name: `Selecionar ${nomeDeposito()}` }).click();
  await expect(page.getByText(`Depósito ativo: ${nomeDeposito()}`)).toBeVisible();
}

async function cadastrarProduto(page) {
  await page.getByRole("button", { name: "Estoque", exact: true }).click();
  await page.getByRole("button", { name: "Novo produto" }).click();
  await page.getByLabel("Código").fill(codigoProduto());
  await page.getByLabel("Nome").fill("Parafuso E2E");
  await page.getByLabel("Categoria", { exact: true }).fill("Fixadores");
  await page.getByLabel("Estoque mínimo").fill("50");
  await page.getByRole("button", { name: "Cadastrar produto" }).click();

  await expect(page.getByRole("heading", { name: "Parafuso E2E" })).toBeVisible();
}

async function movimentar(page, { tipo, quantidade, requerente, destino }) {
  await page.getByRole("button", { name: "Movimentações", exact: true }).click();
  await page.getByRole("button", { name: "Movimentar Parafuso E2E" }).click();
  await page.getByLabel("Tipo").selectOption(tipo);
  await page.getByLabel("Quantidade").fill(String(quantidade));
  if (tipo === "SAIDA") {
    await page.getByLabel("Requerente").fill(requerente);
    await page.getByLabel("Destino").fill(destino);
  }
  await page.getByRole("button", { name: "Registrar movimentação" }).click();
}

test("fluxo completo: depósito, produto, entrada e persistência após recarregar", async ({
  page,
}) => {
  await criarEEntrarNoDeposito(page);
  await cadastrarProduto(page);

  await movimentar(page, { tipo: "ENTRADA", quantidade: 100 });
  await expect(page.getByText("Entrada de 100")).toBeVisible();

  await page.reload();

  await page.getByRole("button", { name: "Estoque", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Parafuso E2E" })).toBeVisible();

  await page.getByRole("button", { name: "Movimentações", exact: true }).click();
  await page.getByRole("button", { name: "Movimentar Parafuso E2E" }).click();
  await expect(page.getByText("Entrada de 100")).toBeVisible();
});

test("saída maior que o saldo é recusada pelo backend", async ({ page }) => {
  await criarEEntrarNoDeposito(page);
  await cadastrarProduto(page);
  await movimentar(page, { tipo: "ENTRADA", quantidade: 70 });

  await movimentar(page, {
    tipo: "SAIDA",
    quantidade: 500,
    requerente: "Ana",
    destino: "Oficina",
  });

  await expect(page.getByText(/Saldo insuficiente/)).toBeVisible();
});

test("saída registra requerente e destino no histórico", async ({ page }) => {
  await criarEEntrarNoDeposito(page);
  await cadastrarProduto(page);
  await movimentar(page, { tipo: "ENTRADA", quantidade: 100 });

  await movimentar(page, {
    tipo: "SAIDA",
    quantidade: 30,
    requerente: "Ana",
    destino: "Oficina",
  });

  await expect(page.getByText("Saída de 30")).toBeVisible();
  await expect(page.getByText(/para\s*Ana/)).toBeVisible();
  await expect(page.getByText(/destino Oficina/)).toBeVisible();
});
