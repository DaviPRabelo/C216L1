import { comCorpo, requisitar } from "./api.js";

export function listarInventarios(almoxarifadoId = null) {
  const parametros = new URLSearchParams();
  if (almoxarifadoId) parametros.set("almoxarifado_id", String(almoxarifadoId));

  const consulta = parametros.toString();
  return requisitar(`/inventarios${consulta ? `?${consulta}` : ""}`);
}

export function obterInventario(id) {
  return requisitar(`/inventarios/${id}`);
}

export function abrirInventario(dados) {
  return requisitar("/inventarios", comCorpo("POST", dados));
}

export function contarItem(inventarioId, produtoId, quantidadeContada) {
  return requisitar(
    `/inventarios/${inventarioId}/itens/${produtoId}`,
    comCorpo("PATCH", { quantidade_contada: quantidadeContada }),
  );
}

export function fecharInventario(id) {
  return requisitar(`/inventarios/${id}/fechar`, { method: "POST" });
}
