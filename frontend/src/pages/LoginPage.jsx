import { useState } from "react";
import { useSessao } from "../context/SessaoContext.jsx";
import { entrar as autenticar, cadastrar } from "../services/auth.js";
import { ehValido, PAPEIS, validarLogin } from "../validation.js";

const CAMPO =
  "w-full rounded border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none";
const ROTULO = "mb-1 block text-sm font-medium text-slate-700";

export default function LoginPage() {
  const { entrar } = useSessao();
  const [criandoConta, setCriandoConta] = useState(false);
  const [valores, setValores] = useState({
    nome: "",
    setor: "",
    email: "",
    senha: "",
    papel: "EMPREGADO",
  });
  const [erros, setErros] = useState({});
  const [falha, setFalha] = useState(null);
  const [enviando, setEnviando] = useState(false);

  function aoMudar(campo, valor) {
    setValores((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function aoEnviar(evento) {
    evento.preventDefault();
    setFalha(null);

    const encontrados = validarLogin(valores);
    if (criandoConta && !valores.nome.trim()) encontrados.nome = "O nome é obrigatório";
    setErros(encontrados);
    if (!ehValido(encontrados)) return;

    setEnviando(true);
    try {
      const operador = criandoConta
        ? await cadastrar({
            nome: valores.nome.trim(),
            setor: valores.setor.trim(),
            email: valores.email.trim(),
            senha: valores.senha,
            papel: valores.papel,
          })
        : await autenticar(valores.email.trim(), valores.senha);
      entrar(operador);
    } catch (erro) {
      setFalha(erro.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900">
            Almoxarifado <span className="text-sky-600">C216</span>
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            {criandoConta ? "Crie seu acesso de operador" : "Entre para controlar o estoque"}
          </p>
        </div>

        <form onSubmit={aoEnviar} className="space-y-4 rounded-lg bg-white p-6 shadow" noValidate>
          {criandoConta && (
            <>
              <div>
                <label htmlFor="nome" className={ROTULO}>
                  Nome
                </label>
                <input
                  id="nome"
                  type="text"
                  value={valores.nome}
                  onChange={(e) => aoMudar("nome", e.target.value)}
                  className={CAMPO}
                />
                {erros.nome && (
                  <p role="alert" className="mt-1 text-sm text-red-600">
                    {erros.nome}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="setor" className={ROTULO}>
                  Setor
                </label>
                <input
                  id="setor"
                  type="text"
                  value={valores.setor}
                  onChange={(e) => aoMudar("setor", e.target.value)}
                  className={CAMPO}
                />
              </div>

              <div>
                <label htmlFor="papel" className={ROTULO}>
                  Papel
                </label>
                <select
                  id="papel"
                  value={valores.papel}
                  onChange={(e) => aoMudar("papel", e.target.value)}
                  className={CAMPO}
                >
                  {PAPEIS.map((p) => (
                    <option key={p.valor} value={p.valor}>
                      {p.rotulo}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-slate-500">
                  Só empregados podem responder por um almoxarifado.
                </p>
              </div>
            </>
          )}

          <div>
            <label htmlFor="email" className={ROTULO}>
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={valores.email}
              onChange={(e) => aoMudar("email", e.target.value)}
              className={CAMPO}
            />
            {erros.email && (
              <p role="alert" className="mt-1 text-sm text-red-600">
                {erros.email}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="senha" className={ROTULO}>
              Senha
            </label>
            <input
              id="senha"
              type="password"
              value={valores.senha}
              onChange={(e) => aoMudar("senha", e.target.value)}
              className={CAMPO}
            />
            {erros.senha && (
              <p role="alert" className="mt-1 text-sm text-red-600">
                {erros.senha}
              </p>
            )}
          </div>

          {falha && (
            <p
              role="alert"
              className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-800"
            >
              {falha}
            </p>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded bg-sky-600 px-4 py-2.5 font-medium text-white hover:bg-sky-700 disabled:opacity-60"
          >
            {enviando ? "Aguarde..." : criandoConta ? "Criar acesso" : "Entrar"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => {
            setCriandoConta((anterior) => !anterior);
            setErros({});
            setFalha(null);
          }}
          className="w-full text-sm text-sky-700 hover:underline"
        >
          {criandoConta ? "Já tenho acesso" : "Não tenho acesso — criar agora"}
        </button>
      </div>
    </div>
  );
}
