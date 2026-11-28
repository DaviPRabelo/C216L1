import { defineConfig, devices } from "@playwright/test";

const PORTA = 4173;
const URL_BASE = `http://localhost:${PORTA}`;

export default defineConfig({
  testDir: "./e2e",
  // Os testes conversam com o backend e o banco reais. Em paralelo eles
  // competem pela mesma base e o front chega a re-renderizar no meio de um
  // preenchimento, por isso a suíte roda em série (são poucos segundos).
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? "list" : "html",
  use: {
    baseURL: URL_BASE,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run build && npm run preview",
    url: URL_BASE,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
