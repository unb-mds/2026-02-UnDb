"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

export default function ListaProgressiva({ itens, id, rotulo, botao, classe, inicial = 12, passo = 12, lista = false }: {
  itens: readonly ReactNode[];
  id: string;
  rotulo: string;
  botao: string;
  classe: string;
  inicial?: number;
  passo?: number;
  lista?: boolean;
}) {
  const [limite, setLimite] = useState(inicial);
  const anterior = useRef(inicial);
  const grupo = useRef<HTMLDivElement>(null);
  const visiveis = itens.slice(0, limite);
  useEffect(() => {
    if (limite > anterior.current) {
      const novo = grupo.current?.querySelector<HTMLElement>(`[data-itens-progressivos] > :nth-child(${anterior.current + 1})`);
      const destino = novo?.matches("a, button") ? novo : novo?.querySelector<HTMLElement>("a, button");
      destino?.focus({ preventScroll: true });
    }
    anterior.current = limite;
  }, [limite]);
  const Elemento = lista ? "ul" : "div";
  return <div ref={grupo} className="flex min-w-0 flex-col gap-4">
    <Elemento id={id} data-itens-progressivos aria-label={lista ? rotulo : undefined} className={classe}>{visiveis}</Elemento>
    <p role="status" aria-atomic="true" className="text-sm text-(--muted)">Mostrando {visiveis.length} de {itens.length} {rotulo.toLocaleLowerCase("pt-BR")}.</p>
    {limite < itens.length && <button type="button" className="button self-start" aria-controls={id} onClick={() => setLimite((valor) => valor + passo)}>{botao}</button>}
  </div>;
}
