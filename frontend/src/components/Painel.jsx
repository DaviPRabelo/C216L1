function Indicador({ rotulo, valor, destaque = false }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <p className="text-xs uppercase tracking-wide text-slate-500">{rotulo}</p>
      <p className={`text-2xl font-bold ${destaque ? "text-amber-600" : "text-slate-900"}`}>
        {valor}
      </p>
    </div>
  );
}

export default function Painel({ produtos }) {
  const emFalta = produtos.filter((p) => p.abaixo_do_minimo).length;
  const unidades = produtos.reduce((soma, p) => soma + p.saldo, 0);
  const categorias = new Set(produtos.map((p) => p.categoria)).size;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Indicador rotulo="Produtos" valor={produtos.length} />
      <Indicador rotulo="Categorias" valor={categorias} />
      <Indicador rotulo="Unidades em estoque" valor={unidades} />
      <Indicador rotulo="Abaixo do mínimo" valor={emFalta} destaque={emFalta > 0} />
    </div>
  );
}
