import { useCallback, useEffect, useState } from "react";
import { CAMPO, Campo } from "../components/Campo.jsx";
import { useSessao } from "../context/SessaoContext.jsx";
import {
  atualizarAlmoxarifado,
  criarAlmoxarifado,
  listarAlmoxarifados,
  removerAlmoxarifado,
} from "../services/almoxarifados.js";

const VAZIO = { nome: "", local: "", responsavel: "" };

export default function AlmoxarifadosPage({ aoEscolher }) {
  const { deposito, selecionarDeposito } = useSessao();

  const [depositos, setDepositos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const [valores, setValores] = useState(VAZIO);
  const [editando, setEditando] = useState(null);
  const [mostrandoForm, setMostrandoForm] = useState(false);
  const [paraExcluir, setParaExcluir] = useState(null);

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

  function abrirNovo() {
    setEditando(null);
    setValores(VAZIO);
    setMostrandoForm(true);
  }

  function abrirEdicao(item) {
    setEditando(item);
    setValores({ nome: item.nome, local: item.local, responsavel: item.responsavel });
    setMostrandoForm(true);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setErro(null);
    if (!valores.nome.trim()) {
      setErro("O nome do almoxarifado é obrigatório");
      return;
    }
    try {
      if (editando) await atualizarAlmoxarifado(editando.id, valores);
      else await criarAlmoxarifado(valores);
      setMostrandoForm(false);
      await carregar();
    } catch (falha) {
      setErro(falha.message);
    }
  }

  async function alternarAtivo(item) {
    setErro(null);
    try {
      await atualizarAlmoxarifado(item.id, { ativo: !item.ativo });
      await carregar();
    } catch (falha) {
      setErro(falha.message);
    }
  }

  async function confirmarExclusao() {
    setErro(null);
    try {
      await removerAlmoxarifado(paraExcluir.id);
      if (deposito && deposito.id === paraExcluir.id) selecionarDeposito(null);
      setParaExcluir(null);
      await carregar();
    } catch (falha) {
      setErro(falha.message);
      setParaExcluir(null);
    }
  }

  function escolher(item) {
    selecionarDeposito({ id: item.id, nome: item.nome, local: item.local });
    if (aoEscolher) aoEscolher(item);
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Almoxarifados</h1>
          <p className="text-sm text-slate-600">
            Escolha em qual depósito você vai trabalhar ou cadastre um novo.
          </p>
        </div>
        <button
          type="button"
          onClick={abrirNovo}
          className="rounded bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
        >
          Novo almoxarifado
        </button>
      </div>

      {erro && (
        <p
          role="alert"
          className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800"
        >
          {erro}
        </p>
      )}

      {mostrandoForm && (
        <form onSubmit={salvar} className="space-y-4 rounded-lg bg-white p-4 shadow" noValidate>
          <h2 className="text-lg font-semibold text-slate-800">
            {editando ? "Editar almoxarifado" : "Novo almoxarifado"}
          </h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <Campo id="nome-almox" rotulo="Nome">
              <input
                id="nome-almox"
                type="text"
                value={valores.nome}
                onChange={(e) => setValores({ ...valores, nome: e.target.value })}
                className={CAMPO}
              />
            </Campo>
            <Campo id="local-almox" rotulo="Local">
              <input
                id="local-almox"
                type="text"
                value={valores.local}
                onChange={(e) => setValores({ ...valores, local: e.target.value })}
                className={CAMPO}
              />
            </Campo>
            <Campo id="responsavel-almox" rotulo="Responsável">
              <input
                id="responsavel-almox"
                type="text"
                value={valores.responsavel}
                onChange={(e) => setValores({ ...valores, responsavel: e.target.value })}
                className={CAMPO}
              />
            </Campo>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="rounded bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
            >
              {editando ? "Salvar alterações" : "Cadastrar"}
            </button>
            <button
              type="button"
              onClick={() => setMostrandoForm(false)}
              className="rounded border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {paraExcluir && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4">
          <p className="text-sm text-red-900">
            Excluir o almoxarifado <strong>{paraExcluir.nome}</strong>?
          </p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={confirmarExclusao}
              className="rounded bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700"
            >
              Confirmar exclusão
            </button>
            <button
              type="button"
              onClick={() => setParaExcluir(null)}
              className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-700"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {carregando ? (
        <p className="p-8 text-center text-sm text-slate-500">Carregando almoxarifados...</p>
      ) : depositos.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          Nenhum almoxarifado cadastrado. Crie o primeiro para começar.
        </p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {depositos.map((item) => (
            <li
              key={item.id}
              className={`flex flex-col justify-between rounded-lg bg-white p-4 shadow ${
                deposito && deposito.id === item.id ? "ring-2 ring-sky-500" : ""
              }`}
            >
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-semibold text-slate-900">{item.nome}</h2>
                  {!item.ativo && (
                    <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-700">
                      Desativado
                    </span>
                  )}
                  {deposito && deposito.id === item.id && (
                    <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-medium text-sky-800">
                      Em uso
                    </span>
                  )}
                </div>
                {item.local && <p className="text-sm text-slate-600">{item.local}</p>}
                {item.responsavel && (
                  <p className="text-xs text-slate-500">Responsável: {item.responsavel}</p>
                )}

                <dl className="mt-3 grid grid-cols-3 gap-2 border-t border-slate-100 pt-3 text-center">
                  <div>
                    <dt className="text-xs text-slate-500">Produtos</dt>
                    <dd className="font-bold text-slate-900">{item.total_produtos}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-500">Unidades</dt>
                    <dd className="font-bold text-slate-900">{item.unidades_em_estoque}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-500">Em falta</dt>
                    <dd
                      className={`font-bold ${
                        item.produtos_em_falta > 0 ? "text-amber-600" : "text-slate-900"
                      }`}
                    >
                      {item.produtos_em_falta}
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => escolher(item)}
                  aria-label={`Selecionar ${item.nome}`}
                  className="rounded bg-sky-600 px-3 py-1.5 text-sm text-white hover:bg-sky-700"
                >
                  Selecionar
                </button>
                <button
                  type="button"
                  onClick={() => abrirEdicao(item)}
                  aria-label={`Editar ${item.nome}`}
                  className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                >
                  Editar
                </button>
                <button
                  type="button"
                  onClick={() => alternarAtivo(item)}
                  className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                >
                  {item.ativo ? "Desativar" : "Reativar"}
                </button>
                <button
                  type="button"
                  onClick={() => setParaExcluir(item)}
                  aria-label={`Excluir ${item.nome}`}
                  className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
                >
                  Excluir
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
