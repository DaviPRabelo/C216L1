export const NOME_MAXIMO = 60;
export const DESCRICAO_MAXIMA = 200;
export const PRECO_MAXIMO = 1_000_000;
export const QUANTIDADE_MAXIMA = 9999;

export const CATEGORIAS = ["Eletrônicos", "Periféricos", "Móveis", "Papelaria", "Outros"];

export function validarNome(nome) {
  const valor = (nome ?? "").trim();
  if (!valor) return "O nome é obrigatório";
  if (valor.length > NOME_MAXIMO) return `O nome deve ter até ${NOME_MAXIMO} caracteres`;
  return null;
}

export function validarDescricao(descricao) {
  const valor = (descricao ?? "").trim();
  if (valor.length > DESCRICAO_MAXIMA) {
    return `A descrição deve ter até ${DESCRICAO_MAXIMA} caracteres`;
  }
  return null;
}

export function validarCategoria(categoria) {
  if (!categoria) return "Escolha uma categoria";
  if (!CATEGORIAS.includes(categoria)) return "Categoria inválida";
  return null;
}

export function validarQuantidade(quantidade) {
  if (quantidade === "" || quantidade === null || quantidade === undefined) {
    return "A quantidade é obrigatória";
  }
  const valor = Number(quantidade);
  if (!Number.isInteger(valor)) return "A quantidade deve ser um número inteiro";
  if (valor < 1) return "A quantidade deve ser pelo menos 1";
  if (valor > QUANTIDADE_MAXIMA) return `A quantidade não pode passar de ${QUANTIDADE_MAXIMA}`;
  return null;
}

export function validarPreco(preco) {
  if (preco === "" || preco === null || preco === undefined) return "O preço é obrigatório";
  const valor = Number(preco);
  if (Number.isNaN(valor)) return "O preço deve ser um número";
  if (valor < 0) return "O preço não pode ser negativo";
  if (valor > PRECO_MAXIMO) return `O preço não pode passar de ${PRECO_MAXIMO}`;
  return null;
}

export function validarItem({ nome, descricao, categoria, quantidade, preco }) {
  const erros = {};
  const validacoes = {
    nome: validarNome(nome),
    descricao: validarDescricao(descricao),
    categoria: validarCategoria(categoria),
    quantidade: validarQuantidade(quantidade),
    preco: validarPreco(preco),
  };
  for (const [campo, erro] of Object.entries(validacoes)) {
    if (erro) erros[campo] = erro;
  }
  return erros;
}

export function ehValido(erros) {
  return Object.keys(erros).length === 0;
}

export function formatarMoeda(valor) {
  return `R$ ${Number(valor).toFixed(2).replace(".", ",")}`;
}
