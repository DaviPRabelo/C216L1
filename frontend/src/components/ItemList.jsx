import { formatarMoeda } from "../validation.js";

export default function ItemList({ itens, onRemover }) {
  if (itens.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
        Nenhum produto cadastrado ainda.
      </p>
    );
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {itens.map((item) => (
        <li
          key={item.id}
          className="flex flex-col justify-between rounded-lg bg-white p-4 shadow transition hover:shadow-md"
        >
          <div className="space-y-2">
            <span className="inline-block rounded-full bg-sky-100 px-2 py-0.5 text-xs font-medium text-sky-800">
              {item.categoria}
            </span>
            <h3 className="font-semibold text-slate-900">{item.nome}</h3>
            {item.descricao && <p className="text-sm text-slate-600">{item.descricao}</p>}
          </div>

          <div className="mt-4 space-y-2 border-t border-slate-100 pt-3">
            <p className="text-xl font-bold text-slate-900">{formatarMoeda(item.preco)}</p>
            <p className="text-xs text-slate-500">
              {item.quantidade} em estoque · subtotal {formatarMoeda(item.quantidade * item.preco)}
            </p>
            <button
              type="button"
              onClick={() => onRemover(item.id)}
              aria-label={`Remover ${item.nome}`}
              className="w-full rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
            >
              Remover
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
