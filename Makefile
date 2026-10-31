PYTHON = python
POETRY = python -m poetry
BACKEND_DIR = backend
FRONTEND_DIR = frontend
NPM = npm


.PHONY: help install run test test-v test-cov test-unit test-integration lint format clean \
        docker-up docker-down docker-logs docker-build docker-ps up-build \
        migrate migration db-shell \
        front-install front-dev front-build front-preview \
        front-lint front-format front-format-check front-test front-test-e2e \
        front-check back-check check-all

help:
	@echo "Comandos disponíveis:"
	@echo ""
	@echo "  Desenvolvimento:"
	@echo "    make install       - Instala dependências do Poetry no backend"
	@echo "    make run           - Inicia o servidor FastAPI com live reload"
	@echo "    make clean         - Remove arquivos temporários e caches"
	@echo ""
	@echo "  Testes:"
	@echo "    make test          - Executa os testes com pytest"
	@echo "    make test-v        - Executa os testes em modo verboso"
	@echo "    make test-cov      - Executa os testes com relatório de cobertura"
	@echo ""
	@echo ""
	@echo "  Frontend:"
	@echo "    make front-install      - Instala as dependências (npm ci)"
	@echo "    make front-dev          - Sobe o Vite em modo desenvolvimento"
	@echo "    make front-build        - Gera o bundle de produção"
	@echo "    make front-lint         - Verifica o lint com Biome"
	@echo "    make front-format       - Formata o código com Biome"
	@echo "    make front-test         - Testes unitários e de integração (Vitest)"
	@echo "    make front-test-e2e     - Testes E2E (Playwright)"
	@echo ""
	@echo "  Validação completa:"
	@echo "    make front-check        - Sequência completa do frontend"
	@echo "    make back-check         - Lint e testes do backend"
	@echo "    make check-all          - Valida backend e frontend"

	@echo "  Docker:"
	@echo "    make docker-build  - Builda as imagens e sobe os containers"
	@echo "    make docker-up     - Sobe os containers"
	@echo "    make docker-down   - Derruba os containers"
	@echo "    make docker-logs   - Acompanha os logs"
	@echo "    make docker-ps     - Lista o status dos containers"
	@echo "    make up-build      - Alias de docker-build"
	@echo ""
	@echo "  Banco de dados:"
	@echo "    make migrate       - Aplica as migrations (alembic upgrade head)"
	@echo "    make migration m=\"msg\" - Gera uma migration nova"
	@echo "    make db-shell      - Abre o psql no container do PostgreSQL"

install:
	cd $(BACKEND_DIR) && $(POETRY) install

run:
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn app.main:app --reload

test:
	cd $(BACKEND_DIR) && $(POETRY) run pytest

test-v:
	cd $(BACKEND_DIR) && $(POETRY) run pytest -v

test-cov:
	cd $(BACKEND_DIR) && $(POETRY) run pytest --cov=app --cov-report=term-missing

lint:
	cd $(BACKEND_DIR) && $(POETRY) run ruff check .

format:
	cd $(BACKEND_DIR) && $(POETRY) run ruff format .

test-unit:
	cd $(BACKEND_DIR) && $(POETRY) run pytest tests/unit

test-integration:
	cd $(BACKEND_DIR) && $(POETRY) run pytest tests/integration

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose up --build -d

docker-ps:
	docker compose ps

# Alias exigido pelo roteiro da prática
up-build: docker-build

migrate:
	cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head

migration:
	cd $(BACKEND_DIR) && $(POETRY) run alembic revision --autogenerate -m "$(m)"

db-shell:
	docker exec -it c216_postgres psql -U admin -d c216_db

front-install:
	cd $(FRONTEND_DIR) && $(NPM) ci

front-dev:
	cd $(FRONTEND_DIR) && $(NPM) run dev

front-build:
	cd $(FRONTEND_DIR) && $(NPM) run build

front-preview:
	cd $(FRONTEND_DIR) && $(NPM) run preview

front-lint:
	cd $(FRONTEND_DIR) && $(NPM) run lint

front-format:
	cd $(FRONTEND_DIR) && $(NPM) run format

front-format-check:
	cd $(FRONTEND_DIR) && $(NPM) run format:check

front-test:
	cd $(FRONTEND_DIR) && $(NPM) run test

front-test-e2e:
	cd $(FRONTEND_DIR) && $(NPM) run test:e2e

# Sequência completa do frontend, na ordem do checklist de entrega
front-check: front-install front-lint front-format-check front-test front-build front-test-e2e

# Lint e testes do backend
back-check: lint test

# Valida o projeto inteiro
check-all: back-check front-check
