import { comCorpo, requisitar } from "./api.js";

export function listarProdutos({
  almoxarifadoId = null,
  categoria = "",
  abaixoDoMinimo = false,
} = {}) {
  const parametros = new URLSearchParams();
  if (almoxarifadoId) parametros.set("almoxarifado_id", String(almoxarifadoId));
  if (categoria) parametros.set("categoria", categoria);
  if (abaixoDoMinimo) parametros.set("abaixo_do_minimo", "true");

  const consulta = parametros.toString();
  return requisitar(`/produtos${consulta ? `?${consulta}` : ""}`);
}

export function listarCategorias(almoxarifadoId = null) {
  const parametros = new URLSearchParams();
  if (almoxarifadoId) parametros.set("almoxarifado_id", String(almoxarifadoId));

  const consulta = parametros.toString();
  return requisitar(`/produtos/categorias${consulta ? `?${consulta}` : ""}`);
}

export function criarProduto(dados) {
  return requisitar("/produtos", comCorpo("POST", dados));
}

export function atualizarProduto(id, dados) {
  return requisitar(`/produtos/${id}`, comCorpo("PUT", dados));
}

export function removerProduto(id) {
  return requisitar(`/produtos/${id}`, { method: "DELETE" });
}
