# Backend — C216 L1

API em FastAPI com Poetry, persistência em PostgreSQL via SQLAlchemy, migrations
com Alembic, testes em Pytest, lint com Ruff e execução em Docker.

## Requisitos

- Python 3.10 ou superior
- Poetry
- Docker e Docker Compose

## Configuração

As credenciais do banco vêm de variáveis de ambiente. Copie o exemplo e ajuste:

```bash
cp .env.example .env
```

| Variável | Descrição |
|---|---|
| `POSTGRES_USER` | usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | senha do PostgreSQL |
| `POSTGRES_DB` | nome do banco |
| `POSTGRES_PORT` | porta publicada no host (padrão 5432) |
| `DATABASE_URL` | montada pelo Compose a partir das anteriores |

O arquivo `.env` não é versionado; apenas o `.env.example`.

## Subindo o projeto

```bash
make up-build    # builda as imagens e sobe API + banco
make docker-ps   # verifica o status
make docker-logs # acompanha os logs
make docker-down # derruba os containers
```

As migrations são aplicadas automaticamente no boot do container da API,
antes do Uvicorn subir.

A API fica em `http://localhost:8000` e a documentação interativa em
`http://localhost:8000/docs`.

## Banco de dados

```bash
make migrate                      # aplica as migrations pendentes
make migration m="minha mudanca"  # gera uma migration nova a partir dos modelos
make db-shell                     # abre o psql no container
```

O Alembic lê a `DATABASE_URL` do ambiente — nenhuma credencial fica no
`alembic.ini`.

## Executando os testes

Os testes de integração precisam do PostgreSQL no ar:

```bash
make docker-up          # sobe o banco
make test               # suíte completa
make test-unit          # apenas unitários (não precisam de banco)
make test-integration   # apenas integração
make test-cov           # com relatório de cobertura
```

### Organização dos testes

| Pasta | Tipo | O que exercita |
|---|---|---|
| `tests/unit/` | unitários | camada de serviço, com repositório falso em memória |
| `tests/integration/` | integração | endpoints via `TestClient`, contra PostgreSQL real |

Os unitários usam um dublê do repositório, então rodam sem banco e em
milissegundos. Os de integração criam o banco `c216_test` automaticamente e
limpam as tabelas entre cada teste.

## Lint

```bash
make lint     # verifica
make format   # formata automaticamente
```

## Integração contínua

O workflow `.github/workflows/ci-backend.yml` roda a cada `push` e
`pull_request`, em dois jobs paralelos:

- **testes** — sobe um serviço PostgreSQL, aplica as migrations e executa os
  dois níveis da suíte em Python 3.10 e 3.12
- **lint** — executa o Ruff

## Estrutura

```
backend/
├── app/
│   ├── main.py              # apenas inicialização e inclusão de routers
│   ├── api/routes/
│   │   └── itens.py         # endpoints do recurso
│   ├── schemas/
│   │   └── item.py          # modelos Pydantic (contratos da API)
│   ├── services/
│   │   └── item.py          # regras de negócio
│   ├── repositories/
│   │   └── item.py          # acesso aos dados via SQLAlchemy
│   ├── models/
│   │   └── item.py          # modelo ORM
│   ├── database/
│   │   ├── base.py          # Base declarativa
│   │   └── session.py       # engine e sessão
│   └── errors.py            # exceções de domínio
├── alembic/
│   └── versions/            # migrations
├── tests/
│   ├── unit/
│   └── integration/
├── alembic.ini
└── pyproject.toml
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/itens` | lista itens; aceita `?nome_contem=` |
| `GET` | `/itens/{item_id}` | busca por id |
| `POST` | `/itens` | cria um item |
| `PUT` | `/itens/{item_id}` | substitui o item inteiro |
| `PATCH` | `/itens/{item_id}` | atualiza apenas os campos informados |
| `DELETE` | `/itens/{item_id}` | remove o item |
