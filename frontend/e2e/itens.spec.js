import { expect, test } from "@playwright/test";

const API = process.env.E2E_API_URL ?? "http://localhost:8000";

// Prefixo exclusivo deste teste. Os testes rodam em paralelo e compartilham o
// mesmo banco, então a limpeza precisa alcançar só o que este teste criou.
let prefixo;

function nomeUnico(sufixo = "") {
  return `${prefixo}${sufixo}`;
}

async function cadastrar(
  page,
  { nome, categoria = "Periféricos", quantidade = "2", preco = "150" },
) {
  await page.getByLabel("Nome").fill(nome);
  await page.getByLabel("Categoria").selectOption(categoria);
  await page.getByLabel("Quantidade").fill(quantidade);
  await page.getByLabel("Preço").fill(preco);
  await page.getByRole("button", { name: "Cadastrar produto" }).click();
}

test.beforeEach(async ({ page }, testInfo) => {
  prefixo = `E2E-w${testInfo.workerIndex}-${Date.now()}`;
  await page.goto("/");
  await expect(page.getByText("Carregando produtos...")).toBeHidden();
});

test.afterEach(async ({ request }) => {
  const itens = await (await request.get(`${API}/itens`)).json();
  for (const item of itens.filter((i) => i.nome.startsWith(prefixo))) {
    await request.delete(`${API}/itens/${item.id}`);
  }
});

test("carrega o catálogo a partir da API", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Cadastrar produto" })).toBeVisible();
  await expect(page.getByRole("heading", { name: /^Produtos \(\d+\)$/ })).toBeVisible();
});

test("o produto cadastrado sobrevive ao recarregamento da página", async ({ page }) => {
  const nome = nomeUnico();

  await cadastrar(page, { nome });
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();

  await page.reload();

  await expect(page.getByRole("heading", { name: nome })).toBeVisible();
});

test("rejeita um nome já cadastrado com a mensagem do backend", async ({ page }) => {
  const nome = nomeUnico();
  await cadastrar(page, { nome });
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();

  await cadastrar(page, { nome, preco: "999" });

  await expect(page.getByRole("alert")).toHaveText("Já existe um item com esse nome");
  await expect(page.getByLabel("Nome")).toHaveValue(nome);
});

test("a remoção também persiste após recarregar", async ({ page }) => {
  const nome = nomeUnico();
  await cadastrar(page, { nome });
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();

  await page.getByRole("button", { name: `Remover ${nome}` }).click();
  await expect(page.getByRole("heading", { name: nome })).toBeHidden();

  await page.reload();

  await expect(page.getByRole("heading", { name: nome })).toBeHidden();
});

test("bloqueia o cadastro incompleto antes de chamar a API", async ({ page }) => {
  await page.getByRole("button", { name: "Cadastrar produto" }).click();

  await expect(page.getByText("O nome é obrigatório")).toBeVisible();
  await expect(page.getByText("Escolha uma categoria")).toBeVisible();
});
