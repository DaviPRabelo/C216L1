const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function requisitar(caminho, opcoes = {}) {
  let resposta;

  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, {
      headers: { "Content-Type": "application/json" },
      ...opcoes,
    });
  } catch {
    throw new Error("Não foi possível conectar ao servidor. Verifique se a API está no ar.");
  }

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}));
    throw new Error(corpo.detail ?? `Erro ${resposta.status} ao falar com o servidor`);
  }

  if (resposta.status === 204) return null;
  return resposta.json();
}

export function comCorpo(metodo, dados) {
  return { method: metodo, body: JSON.stringify(dados) };
}
