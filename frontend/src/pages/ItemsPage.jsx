import ItemForm from "../components/ItemForm.jsx";
import ItemList from "../components/ItemList.jsx";
import { useState } from "react";
import { formatarMoeda } from "../validation.js";

export default function ItemsPage() {
  const [itens, setItens] = useState([]);
  const [proximoId, setProximoId] = useState(1);

  const total = itens.reduce((soma, item) => soma + item.quantidade * item.preco, 0);
  const unidades = itens.reduce((soma, item) => soma + item.quantidade, 0);

  function adicionar(dados) {
    setItens((anteriores) => [...anteriores, { id: proximoId, ...dados }]);
    setProximoId((anterior) => anterior + 1);
  }

  function remover(id) {
    setItens((anteriores) => anteriores.filter((item) => item.id !== id));
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 p-4 sm:p-8">
      <section aria-labelledby="titulo-cadastro" className="space-y-3">
        <h1 id="titulo-cadastro" className="text-2xl font-bold text-slate-900">
          Cadastrar produto
        </h1>
        <ItemForm onAdicionar={adicionar} />
      </section>

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
        <ItemList itens={itens} onRemover={remover} />
      </section>
    </main>
  );
}
