import { comCorpo, requisitar } from "./api.js";

export function listarMovimentacoes(produtoId) {
  return requisitar(`/produtos/${produtoId}/movimentacoes`);
}

export function registrarMovimentacao(produtoId, dados) {
  return requisitar(`/produtos/${produtoId}/movimentacoes`, comCorpo("POST", dados));
}
