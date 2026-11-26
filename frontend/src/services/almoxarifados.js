import { comCorpo, requisitar } from "./api.js";

export function listarAlmoxarifados({ apenasAtivos = false } = {}) {
  const consulta = apenasAtivos ? "?apenas_ativos=true" : "";
  return requisitar(`/almoxarifados${consulta}`);
}

export function criarAlmoxarifado(dados) {
  return requisitar("/almoxarifados", comCorpo("POST", dados));
}

export function atualizarAlmoxarifado(id, dados) {
  return requisitar(`/almoxarifados/${id}`, comCorpo("PATCH", dados));
}

export function removerAlmoxarifado(id) {
  return requisitar(`/almoxarifados/${id}`, { method: "DELETE" });
}
