import os


def _lista(valor: str) -> list[str]:
    return [item.strip() for item in valor.split(",") if item.strip()]


# Origens autorizadas a consumir a API, separadas por vírgula.
# 5173 = Vite em desenvolvimento; 4173 = preview da build, usado pelo Playwright.
CORS_ORIGINS = _lista(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"))
