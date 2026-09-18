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
make test
```

Modo verboso, mostrando cada teste individualmente:

```bash
make test-v
```

Com relatório de cobertura por arquivo:

```bash
make test-cov
```

Para rodar um arquivo ou um teste específico, use o Pytest direto:

```bash
cd backend
python -m poetry run pytest tests/test_services.py
python -m poetry run pytest -k "invalido"
```

### Organização dos testes

Os testes ficam em `backend/tests/`:

| Arquivo | Conteúdo |
|---|---|
| `conftest.py` | fixtures compartilhadas (`repo`, `repo_com_itens`) |
| `test_services.py` | testes unitários da camada de serviço |

São 9 funções de teste, que geram 13 casos — a função de validação é parametrizada
com 5 combinações inválidas.

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
│   ├── errors.py       # exceções de domínio
│   ├── models.py       # modelos Pydantic
│   ├── repository.py   # armazenamento em memória
│   ├── services.py     # regras de negócio
│   └── main.py         # endpoints FastAPI
└── tests/
    ├── conftest.py
    └── test_services.py
```
