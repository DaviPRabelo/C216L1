# Frontend — C216 L1

Interface em React com Vite, estilização com Tailwind CSS, lint e formatação com
Biome, e testes em três níveis: unitários e de integração com Vitest, E2E com
Playwright.

Nesta prática o frontend **não consome a API** — o estado é local, sem
persistência. A integração chega na Prática 7.

## Requisitos

- Node.js 22 ou superior
- npm

## Instalação

```bash
make front-install
```

Usa `npm ci`, que instala exatamente o que está no `package-lock.json` e falha se
ele estiver fora de sincronia com o `package.json`.

## Executando

```bash
make front-dev       # servidor de desenvolvimento (http://localhost:5173)
make front-build     # gera o bundle de produção em dist/
make front-preview   # serve o bundle já buildado (http://localhost:4173)
```

## Testes

```bash
make front-test       # unitários e integração (Vitest)
make front-test-e2e   # E2E (Playwright)
```

Na primeira execução dos E2E é necessário baixar o navegador:

```bash
cd frontend && npx playwright install chromium
```

### Os três níveis

| Pasta | Nível | Ferramenta | O que exercita |
|---|---|---|---|
| `tests/unit/` | unitário | Vitest | funções puras de validação, sem DOM |
| `tests/integration/` | integração | Vitest + Testing Library | componentes renderizados, com interação do usuário |
| `e2e/` | ponta a ponta | Playwright | fluxo completo em Chromium, sobre o bundle buildado |

São 51 testes no Vitest e 5 no Playwright.

O `include` do `vite.config.js` restringe o Vitest às duas primeiras pastas —
sem isso ele tentaria coletar os `.spec.js` do Playwright, que usam outra API.

## Lint e formatação

```bash
make front-lint           # verifica as regras
make front-format         # formata os arquivos
make front-format-check   # verifica a formatação sem alterar
```

O Biome cobre lint, formatação e ordenação de imports numa ferramenta só — o
equivalente do Ruff no backend.

## Validação completa

```bash
make front-check   # instala, lint, formatação, testes, build e E2E
make check-all     # o mesmo, somado ao backend
```

## Integração contínua

O workflow `.github/workflows/ci-frontend.yml` roda a cada `push` e
`pull_request`, em dois jobs encadeados:

- **qualidade** — Biome: lint e verificação de formatação
- **testes** — depende do anterior (`needs`); roda Vitest, build, e então os E2E

## Estrutura

```
frontend/
├── index.html              # único HTML do projeto
├── vite.config.js          # Vite, Tailwind e configuração do Vitest
├── biome.json              # lint e formatação
├── playwright.config.js    # E2E e servidor de preview
├── src/
│   ├── main.jsx            # ponto de entrada, monta o React
│   ├── App.jsx             # layout: cabeçalho, conteúdo e rodapé
│   ├── index.css           # @import "tailwindcss"
│   ├── validation.js       # regras de validação, funções puras
│   ├── components/
│   │   ├── ItemForm.jsx    # formulário de cadastro
│   │   └── ItemList.jsx    # catálogo em grade
│   └── pages/
│       └── ItemsPage.jsx   # estado da aplicação e composição
├── tests/
│   ├── setup.js
│   ├── unit/
│   └── integration/
└── e2e/
```

## Campos do produto

| Campo | Tipo | Validação |
|---|---|---|
| nome | texto | obrigatório, até 60 caracteres |
| categoria | seleção | obrigatório, entre as cinco disponíveis |
| quantidade | número | inteiro, de 1 a 9999 |
| preço | número | de 0 a 1.000.000 |
| descrição | texto | opcional, até 200 caracteres |
