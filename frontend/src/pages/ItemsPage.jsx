import { useCallback, useEffect, useState } from "react";
import ItemForm from "../components/ItemForm.jsx";
import ItemList from "../components/ItemList.jsx";
import { createItem, deleteItem, listItems } from "../services/items.js";
import { formatarMoeda } from "../validation.js";

export default function ItemsPage() {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const total = itens.reduce((soma, item) => soma + item.quantidade * item.preco, 0);
  const unidades = itens.reduce((soma, item) => soma + item.quantidade, 0);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setItens(await listItems());
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function adicionar(dados) {
    setErro(null);
    try {
      const criado = await createItem(dados);
      setItens((anteriores) => [...anteriores, criado]);
    } catch (falha) {
      setErro(falha.message);
      throw falha;
    }
  }

  async function remover(id) {
    setErro(null);
    try {
      await deleteItem(id);
      setItens((anteriores) => anteriores.filter((item) => item.id !== id));
    } catch (falha) {
      setErro(falha.message);
    }
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 p-4 sm:p-8">
      <section aria-labelledby="titulo-cadastro" className="space-y-3">
        <h1 id="titulo-cadastro" className="text-2xl font-bold text-slate-900">
          Cadastrar produto
        </h1>
        <ItemForm onAdicionar={adicionar} />
      </section>

      {erro && (
        <p
          role="alert"
          className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800"
        >
          {erro}
        </p>
      )}

      <section aria-labelledby="titulo-catalogo" className="space-y-4">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-300 pb-2">
          <h2 id="titulo-catalogo" className="text-xl font-semibold text-slate-800">
            Produtos ({itens.length})
          </h2>
          {itens.length > 0 && (
            <p className="text-sm text-slate-600">
              {unidades} unidades · valor em estoque{" "}
              <strong className="text-slate-900">{formatarMoeda(total)}</strong>
            </p>
          )}
        </div>

        {carregando ? (
          <p className="p-8 text-center text-sm text-slate-500">Carregando produtos...</p>
        ) : (
          <ItemList itens={itens} onRemover={remover} />
        )}
      </section>
    </main>
  );
}
