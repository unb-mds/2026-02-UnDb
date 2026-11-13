import type { CSSProperties } from "react";

export function formatarDidatica(valor: number) {
  return valor.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

/** Representa a média de Didática (1 a 5) já agregada pelo backend; não combina outros critérios. */
export default function EstrelasDidatica({ valor }: { valor: number }) {
  const preenchimento = `${Math.min(100, Math.max(0, (valor / 5) * 100))}%`;
  return <span className="stars" role="img" aria-label={`Didática: ${formatarDidatica(valor)} de 5`} style={{ "--fill": preenchimento } as CSSProperties} />;
}
