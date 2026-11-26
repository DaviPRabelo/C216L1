import { useState } from "react";
import { ehValido, TIPOS, validarMovimentacao } from "../validation.js";
import { CAMPO, Campo } from "./Campo.jsx";

export default function MovimentacaoForm({ produto, operador, onRegistrar }) {
  const inicial = {
    tipo: "ENTRADA",
    quantidade: "1",
    responsavel: operador?.nome ?? "",
    requerente: "",
    destino: "",
    observacao: "",
  };
  const [valores, setValores] = useState(inicial);
  const [erros, setErros] = useState({});
  const [enviando, setEnviando] = useState(false);

  const ehSaida = valores.tipo === "SAIDA";

  function aoMudar(campo, valor) {
    setValores((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function aoEnviar(evento) {
    evento.preventDefault();
    const encontrados = validarMovimentacao(valores);
    setErros(encontrados);
    if (!ehValido(encontrados)) return;

    setEnviando(true);
    try {
      await onRegistrar({
        tipo: valores.tipo,
        quantidade: Number(valores.quantidade),
        responsavel: valores.responsavel.trim(),
        requerente: ehSaida ? valores.requerente.trim() : "",
        destino: ehSaida ? valores.destino.trim() : "",
        observacao: valores.observacao.trim(),
      });
      setValores({ ...inicial });
      setErros({});
    } catch {
      // A página exibe a mensagem do backend (saldo insuficiente, por exemplo).
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={aoEnviar} className="space-y-4 rounded-lg bg-white p-4 shadow" noValidate>
      <h3 className="font-semibold text-slate-800">
        Movimentar {produto.codigo} · saldo atual {produto.saldo} {produto.unidade}
      </h3>

      <div className="grid gap-4 sm:grid-cols-3">
        <Campo id="tipo" rotulo="Tipo" erro={erros.tipo}>
          <select
            id="tipo"
            value={valores.tipo}
            onChange={(e) => aoMudar("tipo", e.target.value)}
            className={CAMPO}
          >
            {TIPOS.map((t) => (
              <option key={t.valor} value={t.valor}>
                {t.rotulo}
              </option>
            ))}
          </select>
        </Campo>

        <Campo id="quantidade" rotulo="Quantidade" erro={erros.quantidade}>
          <input
            id="quantidade"
            type="number"
            min="1"
            step="1"
            value={valores.quantidade}
            onChange={(e) => aoMudar("quantidade", e.target.value)}
            className={CAMPO}
          />
        </Campo>

        <Campo id="responsavel" rotulo="Responsável" erro={erros.responsavel}>
          <input
            id="responsavel"
            type="text"
            value={valores.responsavel}
            onChange={(e) => aoMudar("responsavel", e.target.value)}
            className={CAMPO}
          />
        </Campo>
      </div>

      {ehSaida && (
        <div className="grid gap-4 sm:grid-cols-2">
          <Campo id="requerente" rotulo="Requerente" erro={erros.requerente}>
            <input
              id="requerente"
              type="text"
              value={valores.requerente}
              onChange={(e) => aoMudar("requerente", e.target.value)}
              className={CAMPO}
            />
          </Campo>

          <Campo id="destino" rotulo="Destino" erro={erros.destino}>
            <input
              id="destino"
              type="text"
              value={valores.destino}
              onChange={(e) => aoMudar("destino", e.target.value)}
              className={CAMPO}
            />
          </Campo>
        </div>
      )}

      <Campo id="observacao" rotulo="Observação" erro={erros.observacao}>
        <input
          id="observacao"
          type="text"
          value={valores.observacao}
          onChange={(e) => aoMudar("observacao", e.target.value)}
          className={CAMPO}
        />
      </Campo>

      <button
        type="submit"
        disabled={enviando}
        className="rounded bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
      >
        {enviando ? "Registrando..." : "Registrar movimentação"}
      </button>
    </form>
  );
}
