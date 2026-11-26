import { useCallback, useEffect, useState } from "react";
import { useSessao } from "../context/SessaoContext.jsx";
import { listarAlmoxarifados } from "../services/almoxarifados.js";

function Indicador({ rotulo, valor, destaque = false }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <p className="text-xs uppercase tracking-wide text-slate-500">{rotulo}</p>
      <p className={`text-3xl font-bold ${destaque ? "text-amber-600" : "text-slate-900"}`}>
        {valor}
      </p>
    </div>
  );
}

function Atalho({ titulo, descricao, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg bg-white p-4 text-left shadow transition hover:shadow-md"
    >
      <p className="font-semibold text-slate-900">{titulo}</p>
      <p className="mt-1 text-sm text-slate-600">{descricao}</p>
    </button>
  );
}

export default function InicioPage({ aoNavegar }) {
  const { operador, deposito } = useSessao();
  const [depositos, setDepositos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      setDepositos(await listarAlmoxarifados());
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const produtos = depositos.reduce((soma, d) => soma + d.total_produtos, 0);
  const unidades = depositos.reduce((soma, d) => soma + d.unidades_em_estoque, 0);
  const emFalta = depositos.reduce((soma, d) => soma + d.produtos_em_falta, 0);

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Olá, {operador.nome}</h1>
        <p className="text-sm text-slate-600">
          {deposito
            ? `Você está operando o almoxarifado ${deposito.nome}.`
            : "Escolha um almoxarifado para começar a operar."}
        </p>
      </header>

      {erro && (
        <p
          role="alert"
          className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800"
        >
          {erro}
        </p>
      )}

      {carregando ? (
        <p className="p-8 text-center text-sm text-slate-500">Carregando indicadores...</p>
      ) : (
        <section aria-labelledby="titulo-indicadores" className="space-y-3">
          <h2 id="titulo-indicadores" className="text-lg font-semibold text-slate-800">
            Visão geral
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Indicador rotulo="Almoxarifados" valor={depositos.length} />
            <Indicador rotulo="Produtos cadastrados" valor={produtos} />
            <Indicador rotulo="Unidades em estoque" valor={unidades} />
            <Indicador rotulo="Itens em falta" valor={emFalta} destaque={emFalta > 0} />
          </div>
        </section>
      )}

      <section aria-labelledby="titulo-atalhos" className="space-y-3">
        <h2 id="titulo-atalhos" className="text-lg font-semibold text-slate-800">
          O que você quer fazer
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <Atalho
            titulo="Selecionar almoxarifado"
            descricao="Escolher o depósito em que você vai trabalhar."
            onClick={() => aoNavegar("almoxarifados")}
          />
          <Atalho
            titulo="Gerenciar estoque"
            descricao="Cadastrar, editar e excluir produtos do depósito."
            onClick={() => aoNavegar("estoque")}
          />
          <Atalho
            titulo="Registrar movimentação"
            descricao="Lançar entradas e saídas e ver o histórico."
            onClick={() => aoNavegar("movimentacoes")}
          />
        </div>
      </section>
    </main>
  );
}
