import { comCorpo, requisitar } from "./api.js";

export function entrar(email, senha) {
  return requisitar("/auth/login", comCorpo("POST", { email, senha }));
}

export function listarOperadores() {
  return requisitar("/auth/usuarios");
}

export function cadastrar(dados) {
  return requisitar("/auth/registrar", comCorpo("POST", dados));
}
