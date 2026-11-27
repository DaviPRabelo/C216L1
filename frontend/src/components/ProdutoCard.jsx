import CodigoDeBarras from "./CodigoDeBarras.jsx";

export default function ProdutoCard({ produto, onMovimentar, onEditar, onExcluir }) {
  // onMovimentar é opcional: a tela de estoque só cuida do cadastro.
  return (
    <li className="flex flex-col justify-between rounded-lg bg-white p-4 shadow transition hover:shadow-md">
      <div className="space-y-3">
        {produto.foto ? (
          <img
            src={produto.foto}
            alt={`Foto de ${produto.nome}`}
            className="h-32 w-full rounded border border-slate-100 object-cover"
          />
        ) : (
          <div className="flex h-32 w-full items-center justify-center rounded border border-dashed border-slate-200 text-xs text-slate-400">
            Sem foto
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-700">
            {produto.codigo}
          </span>
          <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-medium text-sky-800">
            {produto.categoria}
          </span>
          {produto.abaixo_do_minimo && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
              Abaixo do mínimo
            </span>
          )}
        </div>

        <h3 className="font-semibold text-slate-900">{produto.nome}</h3>
        {produto.descricao && <p className="text-sm text-slate-600">{produto.descricao}</p>}

        <CodigoDeBarras valor={produto.codigo} />
      </div>

      <div className="mt-4 space-y-3 border-t border-slate-100 pt-3">
        <p className="text-2xl font-bold text-slate-900">
          {produto.saldo}{" "}
          <span className="text-sm font-normal text-slate-500">
            {produto.unidade} · mínimo {produto.estoque_minimo}
          </span>
        </p>

        <div className="flex flex-wrap gap-2">
          {onMovimentar && (
            <button
              type="button"
              onClick={() => onMovimentar(produto)}
              aria-label={`Movimentar ${produto.nome}`}
              className="rounded bg-emerald-600 px-3 py-1.5 text-sm text-white hover:bg-emerald-700"
            >
              Movimentar
            </button>
          )}
          <button
            type="button"
            onClick={() => onEditar(produto)}
            aria-label={`Editar ${produto.nome}`}
            className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => onExcluir(produto)}
            aria-label={`Excluir ${produto.nome}`}
            className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
          >
            Excluir
          </button>
        </div>
      </div>
    </li>
  );
}
