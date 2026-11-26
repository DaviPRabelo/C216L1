import { useCallback, useEffect, useState } from "react";
import HistoricoMovimentacoes from "../components/HistoricoMovimentacoes.jsx";
import MovimentacaoForm from "../components/MovimentacaoForm.jsx";
import { useSessao } from "../context/SessaoContext.jsx";
import { listarMovimentacoes, registrarMovimentacao } from "../services/movimentacoes.js";
import { listarProdutos } from "../services/produtos.js";

export default function MovimentacoesPage() {
  const { operador, deposito } = useSessao();

  const [produtos, setProdutos] = useState([]);
  const [selecionado, setSelecionado] = useState(null);
  const [movimentacoes, setMovimentacoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const carregarProdutos = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setProdutos(await listarProdutos({ almoxarifadoId: deposito.id }));
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, [deposito.id]);

  useEffect(() => {
    carregarProdutos();
  }, [carregarProdutos]);

  async function escolher(produto) {
    setSelecionado(produto);
    setErro(null);
    try {
      setMovimentacoes(await listarMovimentacoes(produto.id));
    } catch (falha) {
      setErro(falha.message);
    }
  }

  async function registrar(dados) {
    setErro(null);
    try {
      await registrarMovimentacao(selecionado.id, dados);
      const [lista, historico] = await Promise.all([
        listarProdutos({ almoxarifadoId: deposito.id }),
        listarMovimentacoes(selecionado.id),
      ]);
      setProdutos(lista);
      setMovimentacoes(historico);
      const atualizado = lista.find((p) => p.id === selecionado.id);
      setSelecionado(atualizado || selecionado);
    } catch (falha) {
      setErro(falha.message);
      throw falha;
    }
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Movimentações</h1>
        <p className="text-sm text-slate-600">
          Registre entradas e saídas dos produtos de {deposito.nome}.
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

      <section aria-labelledby="titulo-escolha" className="space-y-3">
        <h2 id="titulo-escolha" className="text-lg font-semibold text-slate-800">
          1. Escolha o produto
        </h2>

        {carregando ? (
          <p className="p-8 text-center text-sm text-slate-500">Carregando produtos...</p>
        ) : produtos.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
            Cadastre um produto no estoque antes de movimentar.
          </p>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {produtos.map((produto) => (
              <li key={produto.id}>
                <button
                  type="button"
                  onClick={() => escolher(produto)}
                  aria-label={`Movimentar ${produto.nome}`}
                  aria-current={selecionado && selecionado.id === produto.id ? "true" : undefined}
                  className={`w-full rounded-lg bg-white p-3 text-left shadow transition hover:shadow-md ${
                    selecionado && selecionado.id === produto.id ? "ring-2 ring-emerald-500" : ""
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs text-slate-600">{produto.codigo}</span>
                    {produto.abaixo_do_minimo && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                        Em falta
                      </span>
                    )}
                  </div>
                  <p className="mt-1 font-medium text-slate-900">{produto.nome}</p>
                  <p className="text-sm text-slate-600">
                    Saldo {produto.saldo} {produto.unidade}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selecionado && (
        <section aria-labelledby="titulo-registro" className="space-y-4">
          <h2 id="titulo-registro" className="text-lg font-semibold text-slate-800">
            2. Registre a movimentação
          </h2>
          <MovimentacaoForm produto={selecionado} operador={operador} onRegistrar={registrar} />

          <h2 className="text-lg font-semibold text-slate-800">Histórico</h2>
          <HistoricoMovimentacoes movimentacoes={movimentacoes} />
        </section>
      )}
    </main>
  );
}
