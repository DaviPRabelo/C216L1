# Almoxarifado C216

Sistema web para controle de estoque de almoxarifados, desenvolvido como Projeto
Final da disciplina **C216 — Sistemas Distribuídos**.

> **Vídeo demonstrativo:** _(link a ser inserido)_

## Tema e objetivo

O sistema atende o problema de **controlar o que entra e o que sai de um
almoxarifado**, mantendo o saldo sempre coerente com o histórico.

A aplicação organiza produtos em depósitos distintos e registra cada entrada e
saída como um lançamento auditável. O saldo de um produto nunca é editado
diretamente: ele só muda por meio de uma movimentação, que fica registrada com
quem a fez, para quem o material foi e para onde foi.

A regra central é que **não se pode retirar mais do que existe**. Uma saída maior
que o saldo é recusada pelo servidor com a quantidade disponível na mensagem.

## Funcionalidades

**Operadores**
- Cadastro e login com senha armazenada em hash (bcrypt)
- O operador logado preenche automaticamente o responsável das movimentações

**Almoxarifados**
- Cadastro, edição, ativação/desativação e exclusão
- Cada depósito exibe total de produtos, unidades em estoque e itens em falta
- O depósito escolhido fica ativo na sessão e filtra todas as demais telas
- Não é possível excluir um depósito que ainda tem produtos

**Produtos**
- CRUD completo pela interface, dentro do depósito ativo
- Código único, unidade de medida (UN, CX, KG, L) e estoque mínimo
- Alerta visual quando o saldo fica abaixo do mínimo
- Filtros por categoria e por "somente abaixo do mínimo"
- Não é possível excluir um produto que já teve movimentações

**Movimentações**
- Entradas e saídas com responsável, observação e histórico por produto
- Saídas exigem **requerente** e **destino**; entradas não
- Saída maior que o saldo é recusada com `409` e mensagem explicativa
- O saldo e o lançamento são gravados na mesma transação

## Tecnologias

| Camada | Ferramentas |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Persistência | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Dependências (backend) | Poetry |
| Qualidade (backend) | Ruff, Pytest |
| Frontend | JavaScript, React 19, Vite, Tailwind CSS 4 |
| Dependências (frontend) | npm |
| Qualidade (frontend) | Biome, Vitest, Testing Library, Playwright |
| Infraestrutura | Docker, Docker Compose, Makefile |
| CI | GitHub Actions |

## Pré-requisitos

- Docker e Docker Compose
- Para rodar os testes fora dos contêineres: Python 3.10+, Poetry, Node.js 22+

## Variáveis de ambiente

Copie o exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

| Variável | Para que serve |
|---|---|
| `POSTGRES_USER` | usuário do banco |
| `POSTGRES_PASSWORD` | senha do banco |
| `POSTGRES_DB` | nome do banco (padrão `almoxarifado`) |
| `POSTGRES_PORT` | porta publicada no host (padrão `5432`) |
| `CORS_ORIGINS` | origens autorizadas a consumir a API, separadas por vírgula |
| `VITE_API_URL` | URL da API vista pelo navegador (padrão `http://localhost:8000`) |

O `.env` **não é versionado**; apenas o `.env.example`. A `DATABASE_URL` é montada
pelo Compose a partir das três primeiras variáveis.

O `VITE_API_URL` precisa ser o endereço que o **navegador** enxerga
(`localhost:8000`), e não o nome do serviço na rede interna do Compose — quem faz
a requisição é a máquina do usuário.

## Executando a aplicação

```bash
make up-build
```

Sobe três contêineres: PostgreSQL, API e interface. As migrações são aplicadas
automaticamente no boot da API, antes do servidor começar a responder.

| Endereço | O que é |
|---|---|
| http://localhost:5173 | interface do sistema |
| http://localhost:8000/docs | documentação interativa da API |

Outros comandos:

```bash
make ps            # status dos contêineres
make docker-logs   # acompanha os logs
make docker-down   # derruba os contêineres (preserva os dados)
```

Para zerar o banco, use `docker compose down -v` — o `-v` remove o volume.

### Primeiro acesso

1. Abra http://localhost:5173
2. Clique em **Não tenho acesso — criar agora** e cadastre um operador
3. Vá em **Almoxarifados**, crie um depósito e clique em **Selecionar**
4. Em **Estoque**, cadastre um produto
5. Em **Movimentações**, escolha o produto e registre uma entrada

## Migrações

```bash
make migrate                     # aplica as migrações pendentes
make db-current                  # mostra a revisão aplicada
make migration m="descricao"     # gera uma migração a partir dos modelos
make db-shell                    # abre o psql no contêiner
```

O Alembic lê a `DATABASE_URL` do ambiente — nenhuma credencial fica no
`alembic.ini`.

## Testes

```bash
make test               # backend: 140 testes (unitários e integração)
make frontend-test      # frontend: 80 testes (unitários e integração)
make e2e                # ponta a ponta: 3 testes em navegador real
make check-all          # tudo acima, mais lint e build
```

Os testes de integração do backend e os E2E precisam do PostgreSQL no ar
(`make docker-up`). Os unitários rodam sem banco.

| Nível | Ferramenta | O que exercita |
|---|---|---|
| Unitário (backend) | Pytest | regras de negócio com repositórios falsos, sem banco |
| Integração (backend) | Pytest + TestClient | endpoints contra PostgreSQL real |
| Unitário (frontend) | Vitest | validações e montagem das requisições, com `fetch` mockado |
| Integração (frontend) | Vitest + Testing Library | telas renderizadas, com os serviços mockados |
| E2E | Playwright | navegador real sobre a build de produção, atravessando API e banco |

O E2E cobre o fluxo completo — criar depósito, cadastrar produto, registrar
entrada, recusar saída sem saldo — e prova a persistência recarregando a página.

## Qualidade

```bash
make lint            # Ruff no backend
make frontend-lint   # Biome no frontend
make fix             # aplica as correções automáticas nos dois
```

## Integração contínua

Dois workflows no GitHub Actions, disparados em `push` e `pull_request`:

- **CI Backend** — Ruff e a suíte do Pytest em Python 3.10 e 3.12, com um serviço
  PostgreSQL
- **CI Frontend** — Biome, Vitest, build e Playwright; sobe PostgreSQL e a API
  antes dos E2E, porque um teste ponta a ponta que não atravessa a API deixa de
  ser ponta a ponta

## Estrutura

```
backend/
├── app/
│   ├── main.py              # inicialização, CORS e registro das rotas
│   ├── api/
│   │   ├── routes/          # endpoints por recurso
│   │   ├── dependencias.py  # injeção dos repositórios
│   │   └── tratamento_de_erros.py
│   ├── schemas/             # contratos de entrada e saída (Pydantic)
│   ├── services/            # regras de negócio
│   ├── repositories/        # acesso aos dados (SQLAlchemy)
│   ├── models/              # modelos ORM
│   ├── database/            # engine e sessão
│   ├── security.py          # hash de senha
│   └── errors.py            # exceções de domínio
├── alembic/versions/        # migrações
└── tests/{unit,integration}

frontend/
├── src/
│   ├── App.jsx              # navegação entre as telas
│   ├── pages/               # Login, Início, Almoxarifados, Estoque, Movimentações
│   ├── components/          # formulários, cartões, histórico
│   ├── services/            # chamadas HTTP
│   ├── context/             # sessão do operador e depósito ativo
│   └── validation.js        # validações da interface
├── tests/{unit,integration}
└── e2e/
```

## Decisões de projeto

**Saldo guardado, histórico como fonte.** O saldo fica no produto para que a
listagem não precise somar movimentações a cada consulta, mas só é alterado
dentro da transação que grava o lançamento. A tabela de movimentações explica
como o saldo chegou ao valor atual.

**Validação nas duas pontas.** O frontend valida para dar resposta imediata; o
backend valida porque é a única fronteira confiável — a API pode ser chamada
diretamente, sem passar pela interface.

**`409` para conflito, `422` para dados inválidos.** Saldo insuficiente e código
duplicado devolvem `409`: o corpo da requisição está correto, o conflito é com o
estado do banco.

**Exceções de domínio traduzidas num lugar só.** Um tratador registrado na
aplicação mapeia cada exceção para o código HTTP correspondente, em vez de
`try/except` repetido em cada rota.

## Limitações conhecidas

O login valida as credenciais contra o banco e guarda o operador no navegador,
mas **não emite token**: as rotas da API continuam abertas a quem as chamar
diretamente. O portão está na interface, não no servidor. Autenticação por token
não era exigida no escopo e foi deixada de fora conscientemente.
