"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";
import { usePathname } from "next/navigation";

/** Anima apenas a chegada: navegação, estado dos filhos e foco continuam com o Next. */
export default function TransicaoPagina({ children }: { children: ReactNode }) {
  const caminho = usePathname();
  const anterior = useRef(caminho);
  const conteudo = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const mudou = anterior.current !== caminho;
    anterior.current = caminho;
    const elemento = conteudo.current;
    const movimento = matchMedia("(prefers-reduced-motion: reduce)");
    if (!mudou || caminho.startsWith("/prototipo") || movimento.matches || !elemento?.animate) return;

    const animacao = elemento.animate(
      [{ opacity: 0.65, transform: "translateY(8px)" }, { opacity: 1, transform: "translateY(0)" }],
      { duration: 240, easing: "cubic-bezier(0.22, 1, 0.36, 1)" },
    );
    const reduzir = () => { if (movimento.matches) animacao.cancel(); };
    movimento.addEventListener("change", reduzir);
    return () => {
      animacao.cancel();
      movimento.removeEventListener("change", reduzir);
    };
  }, [caminho]);

  return <div ref={conteudo} id="conteudo" tabIndex={-1} className="app-content">{children}</div>;
}
