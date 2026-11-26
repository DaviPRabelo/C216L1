import { useEffect, useState } from "react";
import { ehValido, UNIDADES, validarProduto } from "../validation.js";
import { CAMPO, Campo } from "./Campo.jsx";

const VAZIO = {
  codigo: "",
  nome: "",
  descricao: "",
  categoria: "",
  unidade: "UN",
  estoque_minimo: "0",
};

export default function ProdutoForm({ produto, onSalvar, onCancelar }) {
  const [valores, setValores] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    setValores(
      produto
        ? {
            ...produto,
            estoque_minimo: String(produto.estoque_minimo),
            descricao: produto.descricao ?? "",
          }
        : VAZIO,
    );
    setErros({});
  }, [produto]);

  function aoMudar(campo, valor) {
    setValores((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function aoEnviar(evento) {
    evento.preventDefault();
    const encontrados = validarProduto(valores);
    setErros(encontrados);
    if (!ehValido(encontrados)) return;

    setEnviando(true);
    try {
      await onSalvar({
        codigo: valores.codigo.trim(),
        nome: valores.nome.trim(),
        descricao: valores.descricao.trim(),
        categoria: valores.categoria.trim(),
        unidade: valores.unidade,
        estoque_minimo: Number(valores.estoque_minimo),
      });
    } catch {
      // A página exibe a mensagem; o formulário preserva o que foi digitado.
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={aoEnviar} className="space-y-4 rounded-lg bg-white p-4 shadow" noValidate>
      <h2 className="text-lg font-semibold text-slate-800">
        {produto ? `Editar ${produto.codigo}` : "Novo produto"}
      </h2>

      <div className="grid gap-4 sm:grid-cols-2">
        <Campo id="codigo" rotulo="Código" erro={erros.codigo}>
          <input
            id="codigo"
            type="text"
            value={valores.codigo}
            onChange={(e) => aoMudar("codigo", e.target.value)}
            className={CAMPO}
          />
        </Campo>

        <Campo id="nome" rotulo="Nome" erro={erros.nome}>
          <input
            id="nome"
            type="text"
            value={valores.nome}
            onChange={(e) => aoMudar("nome", e.target.value)}
            className={CAMPO}
          />
        </Campo>

        <Campo id="categoria" rotulo="Categoria" erro={erros.categoria}>
          <input
            id="categoria"
            type="text"
            value={valores.categoria}
            onChange={(e) => aoMudar("categoria", e.target.value)}
            className={CAMPO}
          />
        </Campo>

        <Campo id="unidade" rotulo="Unidade" erro={erros.unidade}>
          <select
            id="unidade"
            value={valores.unidade}
            onChange={(e) => aoMudar("unidade", e.target.value)}
            className={CAMPO}
          >
            {UNIDADES.map((u) => (
              <option key={u.valor} value={u.valor}>
                {u.rotulo} ({u.valor})
              </option>
            ))}
          </select>
        </Campo>

        <Campo id="estoque_minimo" rotulo="Estoque mínimo" erro={erros.estoque_minimo}>
          <input
            id="estoque_minimo"
            type="number"
            min="0"
            step="1"
            value={valores.estoque_minimo}
            onChange={(e) => aoMudar("estoque_minimo", e.target.value)}
            className={CAMPO}
          />
        </Campo>
      </div>

      <Campo id="descricao" rotulo="Descrição" erro={erros.descricao}>
        <textarea
          id="descricao"
          rows={2}
          value={valores.descricao}
          onChange={(e) => aoMudar("descricao", e.target.value)}
          className={CAMPO}
        />
      </Campo>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={enviando}
          className="rounded bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700 disabled:opacity-60"
        >
          {enviando ? "Salvando..." : produto ? "Salvar alterações" : "Cadastrar produto"}
        </button>
        <button
          type="button"
          onClick={onCancelar}
          className="rounded border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}
