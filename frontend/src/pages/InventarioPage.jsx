import { useCallback, useEffect, useState } from "react";
import { useSessao } from "../context/SessaoContext.jsx";
import {
  abrirInventario,
  contarItem,
  fecharInventario,
  listarInventarios,
  obterInventario,
} from "../services/inventarios.js";

function formatarData(iso) {
  const [ano, mes, dia] = String(iso).split("-");
  return `${dia}/${mes}/${ano}`;
}

export default function InventarioPage() {
  const { operador, deposito } = useSessao();

  const [historico, setHistorico] = useState([]);
  const [aberto, setAberto] = useState(null);
  const [contagens, setContagens] = useState({});
  const [responsavel, setResponsavel] = useState(operador?.nome ?? "");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const sincronizar = useCallback((inventario) => {
    setAberto(inventario);
    setContagens(
      Object.fromEntries(
        (inventario?.itens ?? []).map((item) => [
          item.produto_id,
          item.quantidade_contada === null ? "" : String(item.quantidade_contada),
        ]),
      ),
    );
  }, []);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const lista = await listarInventarios(deposito.id);
      setHistorico(lista);
      const emAberto = lista.find((i) => i.status === "ABERTO");
      sincronizar(emAberto ? await obterInventario(emAberto.id) : null);
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, [deposito.id, sincronizar]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function abrir(evento) {
    evento.preventDefault();
    setErro(null);
    if (!responsavel.trim()) {
      setErro("Informe quem está fazendo a contagem");
      return;
    }
    try {
      sincronizar(
        await abrirInventario({
          almoxarifado_id: deposito.id,
          responsavel: responsavel.trim(),
        }),
      );
      setHistorico(await listarInventarios(deposito.id));
    } catch (falha) {
      setErro(falha.message);
    }
  }

  async function salvarContagem(produtoId) {
    const digitado = contagens[produtoId];
    if (digitado === "" || digitado === undefined) return;

    setErro(null);
    try {
      sincronizar(await contarItem(aberto.id, produtoId, Number(digitado)));
    } catch (falha) {
      setErro(falha.message);
    }
  }

  async function fechar() {
    setErro(null);
    try {
      await fecharInventario(aberto.id);
      await carregar();
    } catch (falha) {
      setErro(falha.message);
    }
  }

  const porContar = aberto ? aberto.itens.length - aberto.itens_contados : 0;

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Inventário de {deposito.nome}</h1>
        <p className="text-sm text-slate-600">
          A contagem congela o saldo do sistema e compara com o que foi encontrado na prateleira.
        </p>
      </div>

      {erro && (
        <p
          role="alert"
          className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800"
        >
          {erro}
        </p>
      )}

      {carregando ? (
        <p className="p-8 text-center text-sm text-slate-500">Carregando inventário...</p>
      ) : aberto ? (
        <section aria-labelledby="titulo-contagem" className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-white p-4 shadow">
            <div>
              <h2 id="titulo-contagem" className="text-lg font-semibold text-slate-800">
                Contagem de {formatarData(aberto.data)}
              </h2>
              <p className="text-sm text-slate-600">
                Responsável: {aberto.responsavel} · {aberto.itens_contados} de {aberto.itens.length}{" "}
                itens contados
              </p>
            </div>
            <button
              type="button"
              onClick={fechar}
              className="rounded bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800"
            >
              Fechar inventário
            </button>
          </div>

          {porContar > 0 && (
            <p className="text-sm text-slate-600">Faltam {porContar} itens para poder fechar.</p>
          )}

          <div className="overflow-x-auto rounded-lg bg-white shadow">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="p-3">Produto</th>
                  <th className="p-3">Saldo do sistema</th>
                  <th className="p-3">Contado</th>
                  <th className="p-3">Divergência</th>
                </tr>
              </thead>
              <tbody>
                {aberto.itens.map((item) => (
                  <tr key={item.id} className="border-t border-slate-100">
                    <td className="p-3">
                      <span className="font-mono text-xs text-slate-600">
                        {item.produto_codigo}
                      </span>
                      <p className="font-medium text-slate-900">{item.produto_nome}</p>
                    </td>
                    <td className="p-3 text-slate-700">
                      {item.saldo_sistema} {item.unidade}
                    </td>
                    <td className="p-3">
                      <input
                        type="number"
                        min="0"
                        step="1"
                        aria-label={`Contagem de ${item.produto_nome}`}
                        value={contagens[item.produto_id] ?? ""}
                        onChange={(e) =>
                          setContagens((anterior) => ({
                            ...anterior,
                            [item.produto_id]: e.target.value,
                          }))
                        }
                        onBlur={() => salvarContagem(item.produto_id)}
                        className="w-24 rounded border border-slate-300 px-2 py-1"
                      />
                    </td>
                    <td className="p-3">
                      {item.divergencia === null ? (
                        <span className="text-slate-400">—</span>
                      ) : item.divergencia === 0 ? (
                        <span className="font-medium text-emerald-700">confere</span>
                      ) : (
                        <span
                          className={`font-bold ${
                            item.divergencia > 0 ? "text-sky-700" : "text-amber-700"
                          }`}
                        >
                          {item.divergencia > 0 ? `+${item.divergencia}` : item.divergencia}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <form onSubmit={abrir} className="space-y-4 rounded-lg bg-white p-4 shadow" noValidate>
          <h2 className="text-lg font-semibold text-slate-800">Abrir nova contagem</h2>
          <div>
            <label
              htmlFor="responsavel-inventario"
              className="mb-1 block text-sm font-medium text-slate-700"
            >
              Responsável pela contagem
            </label>
            <input
              id="responsavel-inventario"
              type="text"
              value={responsavel}
              onChange={(e) => setResponsavel(e.target.value)}
              className="w-full max-w-sm rounded border border-slate-300 px-3 py-2"
            />
          </div>
          <button
            type="submit"
            className="rounded bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
          >
            Abrir inventário
          </button>
        </form>
      )}

      <section aria-labelledby="titulo-historico" className="space-y-3">
        <h2 id="titulo-historico" className="text-lg font-semibold text-slate-800">
          Contagens anteriores
        </h2>
        {historico.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
            Nenhuma contagem registrada neste almoxarifado.
          </p>
        ) : (
          <ul className="space-y-2">
            {historico.map((item) => (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-white p-3 text-sm shadow"
              >
                <span>
                  <strong>{formatarData(item.data)}</strong> · {item.responsavel}
                </span>
                <span className="flex items-center gap-3">
                  <span className="text-slate-600">
                    {item.itens_divergentes} divergência
                    {item.itens_divergentes === 1 ? "" : "s"}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                      item.status === "ABERTO"
                        ? "bg-amber-100 text-amber-800"
                        : "bg-slate-200 text-slate-700"
                    }`}
                  >
                    {item.status === "ABERTO" ? "Aberto" : "Fechado"}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
