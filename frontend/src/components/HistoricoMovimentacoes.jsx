function formatarData(iso) {
  const data = new Date(iso);
  const dois = (numero) => String(numero).padStart(2, "0");
  return `${dois(data.getDate())}/${dois(data.getMonth() + 1)}/${data.getFullYear()} ${dois(
    data.getHours(),
  )}:${dois(data.getMinutes())}`;
}

export default function HistoricoMovimentacoes({ movimentacoes }) {
  if (movimentacoes.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
        Nenhuma movimentação registrada.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {movimentacoes.map((m) => (
        <li key={m.id} className="rounded-lg bg-white p-3 text-sm shadow">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                m.tipo === "ENTRADA"
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {m.tipo === "ENTRADA" ? "Entrada" : "Saída"} de {m.quantidade}
            </span>
            <span className="text-xs text-slate-500">{formatarData(m.criada_em)}</span>
          </div>
          <p className="mt-1 text-slate-700">
            Registrado por <strong>{m.responsavel}</strong>
            {m.requerente && (
              <>
                {" · "}para <strong>{m.requerente}</strong>
              </>
            )}
            {m.destino && <> · destino {m.destino}</>}
          </p>
          {m.observacao && <p className="text-slate-500">{m.observacao}</p>}
        </li>
      ))}
    </ul>
  );
}
