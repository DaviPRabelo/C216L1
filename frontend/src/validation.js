export const UNIDADES = [
  { valor: "UN", rotulo: "Unidade" },
  { valor: "CX", rotulo: "Caixa" },
  { valor: "KG", rotulo: "Quilo" },
  { valor: "L", rotulo: "Litro" },
];

export const TIPOS = [
  { valor: "ENTRADA", rotulo: "Entrada" },
  { valor: "SAIDA", rotulo: "Saída" },
];

function texto(valor) {
  return (valor ?? "").trim();
}

export function validarProduto({ codigo, nome, descricao, categoria, unidade, estoque_minimo }) {
  const erros = {};

  if (!texto(codigo)) erros.codigo = "O código é obrigatório";
  else if (texto(codigo).length > 20) erros.codigo = "O código deve ter até 20 caracteres";

  if (!texto(nome)) erros.nome = "O nome é obrigatório";
  else if (texto(nome).length > 100) erros.nome = "O nome deve ter até 100 caracteres";

  if (texto(descricao).length > 200) erros.descricao = "A descrição deve ter até 200 caracteres";

  if (!texto(categoria)) erros.categoria = "A categoria é obrigatória";
  else if (texto(categoria).length > 50) erros.categoria = "A categoria deve ter até 50 caracteres";

  if (!UNIDADES.some((u) => u.valor === unidade)) erros.unidade = "Escolha uma unidade";

  const minimo = Number(estoque_minimo);
  if (estoque_minimo === "" || Number.isNaN(minimo) || !Number.isInteger(minimo)) {
    erros.estoque_minimo = "Informe um número inteiro";
  } else if (minimo < 0) {
    erros.estoque_minimo = "O estoque mínimo não pode ser negativo";
  }

  return erros;
}

export function validarMovimentacao({ tipo, quantidade, responsavel, requerente, destino }) {
  const erros = {};

  if (!TIPOS.some((t) => t.valor === tipo)) erros.tipo = "Escolha o tipo";

  const total = Number(quantidade);
  if (quantidade === "" || Number.isNaN(total) || !Number.isInteger(total)) {
    erros.quantidade = "Informe um número inteiro";
  } else if (total <= 0) {
    erros.quantidade = "A quantidade deve ser maior que zero";
  }

  if (!texto(responsavel)) erros.responsavel = "O responsável é obrigatório";

  if (tipo === "SAIDA") {
    if (!texto(requerente)) erros.requerente = "Toda saída precisa do requerente";
    if (!texto(destino)) erros.destino = "Toda saída precisa do destino";
  }

  return erros;
}

export function validarLogin({ email, senha }) {
  const erros = {};

  const endereco = texto(email);
  if (!endereco) erros.email = "O e-mail é obrigatório";
  else if (!endereco.includes("@")) erros.email = "Informe um e-mail válido";

  if (!senha) erros.senha = "A senha é obrigatória";

  return erros;
}

export function ehValido(erros) {
  return Object.keys(erros).length === 0;
}
