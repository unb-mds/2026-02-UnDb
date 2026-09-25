"use client";

import { useEffect, useState } from "react";

/** Atrasa a propagação de um valor — usado para não buscar a cada tecla digitada. */
export function useDebouncedValue<T>(valor: T, atrasoMs = 300): T {
  const [valorAtrasado, setValorAtrasado] = useState(valor);

  useEffect(() => {
    const temporizador = setTimeout(() => setValorAtrasado(valor), atrasoMs);
    return () => clearTimeout(temporizador);
  }, [valor, atrasoMs]);

  return valorAtrasado;
}
