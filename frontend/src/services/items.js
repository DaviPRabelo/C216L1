const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function requisitar(caminho, opcoes = {}) {
  let resposta;

  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, {
      headers: { "Content-Type": "application/json" },
      ...opcoes,
    });
  } catch {
    throw new Error("Não foi possível conectar à API. Verifique se o servidor está no ar.");
  }

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}));
    throw new Error(corpo.detail ?? `Erro ${resposta.status} ao falar com a API`);
  }

  if (resposta.status === 204) return null;
  return resposta.json();
}

export function listItems() {
  return requisitar("/itens");
}

export function createItem(dados) {
  return requisitar("/itens", {
    method: "POST",
    body: JSON.stringify(dados),
  });
}

export function deleteItem(id) {
  return requisitar(`/itens/${id}`, { method: "DELETE" });
}
