import { expect, test } from "@playwright/test";

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

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("exibe o catálogo vazio", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Cadastrar produto" })).toBeVisible();
  await expect(page.getByText("Nenhum produto cadastrado ainda.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Produtos (0)" })).toBeVisible();
});

test("cadastra um produto e exibe no catálogo", async ({ page }) => {
  await page.getByLabel("Nome").fill("Teclado");
  await page.getByLabel("Categoria").selectOption("Periféricos");
  await page.getByLabel("Quantidade").fill("2");
  await page.getByLabel("Preço").fill("150");
  await page.getByLabel("Descrição").fill("Mecânico ABNT2");
  await page.getByRole("button", { name: "Cadastrar produto" }).click();

  await expect(page.getByRole("heading", { name: "Teclado" })).toBeVisible();
  await expect(page.getByText("Mecânico ABNT2")).toBeVisible();
  await expect(page.getByText("R$ 150,00")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Produtos (1)" })).toBeVisible();
});

test("impede o cadastro incompleto", async ({ page }) => {
  await page.getByRole("button", { name: "Cadastrar produto" }).click();

  await expect(page.getByText("O nome é obrigatório")).toBeVisible();
  await expect(page.getByText("Escolha uma categoria")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Produtos (0)" })).toBeVisible();
});

test("soma o valor em estoque de vários produtos", async ({ page }) => {
  await cadastrar(page, { nome: "Teclado", quantidade: "2", preco: "150" });
  await cadastrar(page, { nome: "Monitor", quantidade: "3", preco: "900" });

  await expect(page.getByText("R$ 3000,00")).toBeVisible();
  await expect(page.getByText(/5 unidades/)).toBeVisible();
});

test("remove o produto correto do meio do catálogo", async ({ page }) => {
  for (const nome of ["Teclado", "Monitor", "Mouse"]) {
    await cadastrar(page, { nome });
  }

  await page.getByRole("button", { name: "Remover Monitor" }).click();

  await expect(page.getByRole("heading", { name: "Teclado" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Mouse" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Monitor" })).toBeHidden();
  await expect(page.getByRole("heading", { name: "Produtos (2)" })).toBeVisible();
});
