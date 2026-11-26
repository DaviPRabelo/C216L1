import { createContext, useCallback, useContext, useState } from "react";

const CHAVE_OPERADOR = "almoxarifado.operador";
const CHAVE_DEPOSITO = "almoxarifado.deposito";

const SessaoContext = createContext(null);

function ler(chave) {
  try {
    const guardado = localStorage.getItem(chave);
    return guardado ? JSON.parse(guardado) : null;
  } catch {
    // Aba anônima ou armazenamento bloqueado.
    return null;
  }
}

function gravar(chave, valor) {
  try {
    if (valor === null) localStorage.removeItem(chave);
    else localStorage.setItem(chave, JSON.stringify(valor));
  } catch {
    // Sem persistência, vale só para esta aba.
  }
}

export function ProvedorDeSessao({ children }) {
  const [operador, setOperador] = useState(() => ler(CHAVE_OPERADOR));
  const [deposito, setDeposito] = useState(() => ler(CHAVE_DEPOSITO));

  const entrar = useCallback((dados) => {
    setOperador(dados);
    gravar(CHAVE_OPERADOR, dados);
  }, []);

  const sair = useCallback(() => {
    setOperador(null);
    setDeposito(null);
    gravar(CHAVE_OPERADOR, null);
    gravar(CHAVE_DEPOSITO, null);
  }, []);

  const selecionarDeposito = useCallback((escolhido) => {
    setDeposito(escolhido);
    gravar(CHAVE_DEPOSITO, escolhido);
  }, []);

  return (
    <SessaoContext.Provider value={{ operador, deposito, entrar, sair, selecionarDeposito }}>
      {children}
    </SessaoContext.Provider>
  );
}

export function useSessao() {
  const contexto = useContext(SessaoContext);
  if (contexto === null) {
    throw new Error("useSessao precisa estar dentro de ProvedorDeSessao");
  }
  return contexto;
}
