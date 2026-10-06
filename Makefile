
PYTHON = python
POETRY = python -m poetry
BACKEND_DIR = backend

.PHONY: help install run test test-v test-cov clean \
        docker-up docker-down docker-logs docker-build docker-ps

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
	@echo "  Docker:"
	@echo "    make docker-build  - Builda as imagens e sobe os containers"
	@echo "    make docker-up     - Sobe os containers"
	@echo "    make docker-down   - Derruba os containers"
	@echo "    make docker-logs   - Acompanha os logs"
	@echo "    make docker-ps     - Lista o status dos containers"

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
