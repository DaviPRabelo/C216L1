import JsBarcode from "jsbarcode";
import { useEffect, useRef } from "react";

/**
 * Desenha o código do produto como barras Code 128.
 * O SVG é gerado pelo JsBarcode diretamente no elemento, sem imagem externa.
 */
export default function CodigoDeBarras({ valor, altura = 40 }) {
  const referencia = useRef(null);

  useEffect(() => {
    if (!referencia.current || !valor) return;
    try {
      JsBarcode(referencia.current, valor, {
        format: "CODE128",
        height: altura,
        width: 1.4,
        margin: 0,
        displayValue: true,
        fontSize: 12,
        background: "transparent",
      });
    } catch {
      // Código fora do alfabeto suportado: a tela segue sem as barras.
    }
  }, [valor, altura]);

  if (!valor) return null;

  return (
    <svg
      ref={referencia}
      role="img"
      aria-label={`Código de barras ${valor}`}
      className="w-full max-w-[200px]"
    />
  );
}
