import { useState } from "react";
import { useSessao } from "./context/SessaoContext.jsx";
import AlmoxarifadosPage from "./pages/AlmoxarifadosPage.jsx";
import EstoquePage from "./pages/EstoquePage.jsx";
import InicioPage from "./pages/InicioPage.jsx";
import InventarioPage from "./pages/InventarioPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import MovimentacoesPage from "./pages/MovimentacoesPage.jsx";
import { PAPEIS } from "./validation.js";

// Telas marcadas com `exigeDeposito` só fazem sentido com um almoxarifado escolhido.
const TELAS = [
  { id: "inicio", rotulo: "Início", exigeDeposito: false },
  { id: "almoxarifados", rotulo: "Almoxarifados", exigeDeposito: false },
  { id: "estoque", rotulo: "Estoque", exigeDeposito: true },
  { id: "movimentacoes", rotulo: "Movimentações", exigeDeposito: true },
  { id: "inventario", rotulo: "Inventário", exigeDeposito: true },
];

export default function App() {
  const { operador, deposito, sair } = useSessao();
  const [tela, setTela] = useState("inicio");

  if (!operador) return <LoginPage />;

  const atual = TELAS.find((t) => t.id === tela) ?? TELAS[0];
  const papel = PAPEIS.find((p) => p.valor === operador.papel);
  const precisaEscolher = atual.exigeDeposito && !deposito;

  function conteudo() {
    if (precisaEscolher) return <AlmoxarifadosPage aoEscolher={() => setTela(tela)} />;
    if (tela === "almoxarifados")
      return <AlmoxarifadosPage aoEscolher={() => setTela("estoque")} />;
    if (tela === "estoque") return <EstoquePage />;
    if (tela === "movimentacoes") return <MovimentacoesPage />;
    if (tela === "inventario") return <InventarioPage />;
    return <InicioPage aoNavegar={setTela} />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      <header className="bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <span className="text-lg font-bold tracking-tight">
            Almoxarifado <span className="text-sky-400">C216</span>
          </span>

          <nav aria-label="Principal" className="flex flex-wrap gap-1">
            {TELAS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTela(t.id)}
                aria-current={tela === t.id ? "page" : undefined}
                className={`rounded px-3 py-1.5 text-sm transition ${
                  tela === t.id ? "bg-sky-600 text-white" : "text-slate-300 hover:bg-slate-800"
                }`}
              >
                {t.rotulo}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-300">
              {operador.nome}
              {operador.setor && ` · ${operador.setor}`}
            </span>
            {papel && (
              <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-sky-300">
                {papel.rotulo}
              </span>
            )}
            <button
              type="button"
              onClick={sair}
              className="rounded border border-slate-600 px-3 py-1 hover:bg-slate-800"
            >
              Sair
            </button>
          </div>
        </div>

        {deposito && (
          <div className="border-t border-slate-800 bg-slate-950">
            <div className="mx-auto max-w-6xl px-4 py-1.5 text-xs text-slate-400">
              Depósito ativo: <strong className="text-slate-200">{deposito.nome}</strong>
              {deposito.local && ` · ${deposito.local}`}
            </div>
          </div>
        )}
      </header>

      <div className="flex-1">
        {precisaEscolher && (
          <p className="mx-auto max-w-6xl px-4 pt-4 text-sm text-slate-600">
            Escolha um almoxarifado para continuar.
          </p>
        )}
        {conteudo()}
      </div>

      <footer className="bg-slate-900 py-3 text-center text-xs text-slate-400">
        C216 Sistemas Distribuídos — Projeto Final
      </footer>
    </div>
  );
}
