# Variáveis
PYTHON = python
POETRY = python -m poetry
BACKEND_DIR = backend

.PHONY: help install run test clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala dependências do Poetry no backend"
	@echo "  make run      - Inicia o servidor FastAPI com live reload"
	@echo "  make test     - Executa os testes automatizados com pytest"
	@echo "  make clean    - Remove arquivos temporários e caches"

install:
	cd $(BACKEND_DIR) && $(POETRY) install

run:
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn app.main:app --reload

test:
	cd $(BACKEND_DIR) && $(POETRY) run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	
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