import { useState } from "react";
import { CATEGORIAS, ehValido, validarItem } from "../validation.js";

const VAZIO = { nome: "", descricao: "", categoria: "", quantidade: "1", preco: "" };

const ESTILO_CAMPO =
  "w-full rounded border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none";
const ESTILO_ROTULO = "mb-1 block text-sm font-medium text-slate-700";

function Erro({ mensagem }) {
  if (!mensagem) return null;
  return (
    <p role="alert" className="mt-1 text-sm text-red-600">
      {mensagem}
    </p>
  );
}

export default function ItemForm({ onAdicionar }) {
  const [valores, setValores] = useState(VAZIO);
  const [erros, setErros] = useState({});

  function aoMudar(campo, valor) {
    setValores((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function aoEnviar(evento) {
    evento.preventDefault();
    const encontrados = validarItem(valores);
    setErros(encontrados);
    if (!ehValido(encontrados)) return;

    onAdicionar({
      nome: valores.nome.trim(),
      descricao: valores.descricao.trim(),
      categoria: valores.categoria,
      quantidade: Number(valores.quantidade),
      preco: Number(valores.preco),
    });
    setValores(VAZIO);
    setErros({});
  }

  return (
    <form onSubmit={aoEnviar} className="space-y-4 rounded-lg bg-white p-4 shadow" noValidate>
      <div>
        <label htmlFor="nome" className={ESTILO_ROTULO}>
          Nome
        </label>
        <input
          id="nome"
          type="text"
          value={valores.nome}
          onChange={(e) => aoMudar("nome", e.target.value)}
          className={ESTILO_CAMPO}
        />
        <Erro mensagem={erros.nome} />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label htmlFor="categoria" className={ESTILO_ROTULO}>
            Categoria
          </label>
          <select
            id="categoria"
            value={valores.categoria}
            onChange={(e) => aoMudar("categoria", e.target.value)}
            className={ESTILO_CAMPO}
          >
            <option value="">Selecione...</option>
            {CATEGORIAS.map((categoria) => (
              <option key={categoria} value={categoria}>
                {categoria}
              </option>
            ))}
          </select>
          <Erro mensagem={erros.categoria} />
        </div>

        <div>
          <label htmlFor="quantidade" className={ESTILO_ROTULO}>
            Quantidade
          </label>
          <input
            id="quantidade"
            type="number"
            min="1"
            step="1"
            value={valores.quantidade}
            onChange={(e) => aoMudar("quantidade", e.target.value)}
            className={ESTILO_CAMPO}
          />
          <Erro mensagem={erros.quantidade} />
        </div>

        <div>
          <label htmlFor="preco" className={ESTILO_ROTULO}>
            Preço
          </label>
          <input
            id="preco"
            type="number"
            min="0"
            step="0.01"
            value={valores.preco}
            onChange={(e) => aoMudar("preco", e.target.value)}
            className={ESTILO_CAMPO}
          />
          <Erro mensagem={erros.preco} />
        </div>
      </div>

      <div>
        <label htmlFor="descricao" className={ESTILO_ROTULO}>
          Descrição
        </label>
        <textarea
          id="descricao"
          rows={3}
          value={valores.descricao}
          onChange={(e) => aoMudar("descricao", e.target.value)}
          className={ESTILO_CAMPO}
        />
        <Erro mensagem={erros.descricao} />
      </div>

      <button
        type="submit"
        className="w-full rounded bg-sky-600 px-4 py-2.5 font-medium text-white hover:bg-sky-700 sm:w-auto"
      >
        Cadastrar produto
      </button>
    </form>
  );
}
