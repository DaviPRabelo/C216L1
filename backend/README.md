# Backend — C216 L1

API em FastAPI com Poetry, testes em Pytest, lint com Ruff e execução em Docker.

## Requisitos

- Python 3.10 ou superior
- Poetry
- Docker e Docker Compose (opcional, para rodar em container)

## Instalação

```bash
make install
```

Instala as dependências de produção e de desenvolvimento no ambiente virtual do Poetry.

## Executando a API

```bash
make run
```

Sobe o servidor em `http://localhost:8000` com live reload.
A documentação interativa fica em `http://localhost:8000/docs`.

### Via Docker

```bash
make docker-build   # builda as imagens e sobe os containers
make docker-ps      # verifica o status
make docker-logs    # acompanha os logs
make docker-down    # derruba os containers
```

## Executando os testes

```bash
make test               # suíte completa
make test-unit          # apenas unitários
make test-integration   # apenas integração
make test-cov           # com relatório de cobertura
```

Para rodar um teste específico:

```bash
cd backend
python -m poetry run pytest tests/unit -k "invalido"
```

### Organização dos testes

A suíte é dividida em dois níveis da pirâmide:

| Pasta | Tipo | O que exercita |
|---|---|---|
| `tests/unit/` | unitários | camada de serviço, sem HTTP |
| `tests/integration/` | integração | todos os endpoints, via `TestClient` |

São 28 testes: 13 unitários e 15 de integração. Fixtures compartilhadas ficam em
`tests/conftest.py`; a do `TestClient`, com repositório isolado por teste, em
`tests/integration/conftest.py`.

## Lint

```bash
make lint     # verifica
make format   # formata automaticamente
```

## Integração contínua

O workflow `.github/workflows/ci-backend.yml` roda a cada `push` e `pull_request`,
em dois jobs paralelos:

- **testes** — executa a suíte em Python 3.10 e 3.12
- **lint** — executa o Ruff

## Estrutura

```
backend/
├── app/
│   ├── main.py              # apenas inicialização e inclusão de routers
│   ├── api/routes/
│   │   └── itens.py         # endpoints do recurso
│   ├── schemas/
│   │   └── item.py          # modelos Pydantic
│   ├── services/
│   │   └── item.py          # regras de negócio
│   ├── repository.py        # armazenamento em memória
│   └── errors.py            # exceções de domínio
└── tests/
    ├── conftest.py
    ├── unit/
    └── integration/
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

Documentação interativa em `http://localhost:8000/docs`.
