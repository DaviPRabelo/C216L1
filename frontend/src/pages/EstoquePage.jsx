import { useCallback, useEffect, useState } from "react";
import Painel from "../components/Painel.jsx";
import ProdutoCard from "../components/ProdutoCard.jsx";
import ProdutoForm from "../components/ProdutoForm.jsx";
import { useSessao } from "../context/SessaoContext.jsx";
import { listarAlmoxarifados } from "../services/almoxarifados.js";
import {
  atualizarProduto,
  criarProduto,
  listarCategorias,
  listarProdutos,
  removerProduto,
} from "../services/produtos.js";

export default function EstoquePage() {
  const { deposito } = useSessao();

  const [produtos, setProdutos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [depositos, setDepositos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const [categoria, setCategoria] = useState("");
  const [abaixoDoMinimo, setAbaixoDoMinimo] = useState(false);
  const [formulario, setFormulario] = useState(null);
  const [paraExcluir, setParaExcluir] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const [lista, nomes] = await Promise.all([
        listarProdutos({ almoxarifadoId: deposito.id, categoria, abaixoDoMinimo }),
        listarCategorias(deposito.id),
      ]);
      setProdutos(lista);
      setCategorias(nomes);
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, [deposito.id, categoria, abaixoDoMinimo]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  // Os depósitos ativos alimentam o seletor do formulário de cadastro.
  useEffect(() => {
    listarAlmoxarifados({ apenasAtivos: true })
      .then(setDepositos)
      .catch((falha) => setErro(falha.message));
  }, []);

  async function salvar(dados) {
    setErro(null);
    try {
      if (formulario === "novo") await criarProduto(dados);
      else await atualizarProduto(formulario.id, dados);
      setFormulario(null);
      await carregar();
    } catch (falha) {
      setErro(falha.message);
      throw falha;
    }
  }

  async function confirmarExclusao() {
    setErro(null);
    try {
      await removerProduto(paraExcluir.id);
      setParaExcluir(null);
      await carregar();
    } catch (falha) {
      setErro(falha.message);
      setParaExcluir(null);
    }
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Estoque de {deposito.nome}</h1>
        <p className="text-sm text-slate-600">
          Cadastre, edite e remova os produtos deste almoxarifado.
        </p>
      </div>

      <Painel produtos={produtos} />

      {erro && (
        <p
          role="alert"
          className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800"
        >
          {erro}
        </p>
      )}

      <section className="flex flex-wrap items-end gap-4 rounded-lg bg-white p-4 shadow">
        <div>
          <label
            htmlFor="filtro-categoria"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Filtrar por categoria
          </label>
          <select
            id="filtro-categoria"
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            className="rounded border border-slate-300 px-3 py-2"
          >
            <option value="">Todas</option>
            {categorias.map((nome) => (
              <option key={nome} value={nome}>
                {nome}
              </option>
            ))}
          </select>
        </div>

        <label className="flex items-center gap-2 pb-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={abaixoDoMinimo}
            onChange={(e) => setAbaixoDoMinimo(e.target.checked)}
            className="h-4 w-4"
          />
          Só abaixo do mínimo
        </label>

        <button
          type="button"
          onClick={() => setFormulario("novo")}
          className="ml-auto rounded bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
        >
          Novo produto
        </button>
      </section>

      {formulario && (
        <ProdutoForm
          produto={formulario === "novo" ? null : formulario}
          depositos={depositos}
          depositoAtivoId={deposito.id}
          onSalvar={salvar}
          onCancelar={() => setFormulario(null)}
        />
      )}

      {paraExcluir && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4">
          <p className="text-sm text-red-900">
            Excluir <strong>{paraExcluir.nome}</strong> ({paraExcluir.codigo})?
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

      <section aria-labelledby="titulo-estoque" className="space-y-4">
        <h2
          id="titulo-estoque"
          className="border-b border-slate-300 pb-2 text-xl font-semibold text-slate-800"
        >
          Produtos ({produtos.length})
        </h2>

        {carregando ? (
          <p className="p-8 text-center text-sm text-slate-500">Carregando estoque...</p>
        ) : produtos.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
            Nenhum produto encontrado neste almoxarifado.
          </p>
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {produtos.map((produto) => (
              <ProdutoCard
                key={produto.id}
                produto={produto}
                onEditar={setFormulario}
                onExcluir={setParaExcluir}
              />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
