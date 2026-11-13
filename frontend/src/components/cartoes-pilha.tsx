"use client";

import Link from "next/link";
import { useState } from "react";
import Icone from "./icone";

export type ItemPilha = {
  id: string;
  href: string;
  codigo: string;
  titulo: string;
  /** Etiquetas do rodapé; `rotulo` é um prefixo só para leitores de tela. */
  tags: { texto: string; rotulo?: string }[];
  /** Texto só para leitores de tela, descrevendo a ação do cartão. */
  acao: string;
};

const TONS = ["verde", "azul", "claro", "escuro"] as const;

/**
 * Galeria expansível (home): os cartões ficam lado a lado e o cartão sob o mouse (ou com foco)
 * cresce enquanto os demais encolhem, cortando o conteúdo pela direita.
 */
export default function CartoesPilha({ itens, rotulo }: { itens: ItemPilha[]; rotulo: string }) {
  const [passando, setPassando] = useState<number | null>(null);
  return (
    <ul aria-label={rotulo} className="pilha" onMouseLeave={() => setPassando(null)}>
      {itens.map((item, indice) => (
        <li
          key={item.id}
          className="min-w-0"
          style={{ flexGrow: passando === null ? 1 : passando === indice ? 2 : 0.5 }}
          onMouseEnter={() => setPassando(indice)}
          onFocusCapture={() => setPassando(indice)}
          onBlurCapture={() => setPassando(null)}
        >
          <Link href={item.href} className="pilha-card" data-tom={TONS[indice % TONS.length]}>
            <span className="pilha-codigo"><span className="sr-only">Código da disciplina: </span>{item.codigo}</span>
            <h3>{item.titulo}</h3>
            <span className="flex flex-wrap gap-2">
              {item.tags.map((tag) => <span key={tag.texto} className="pilha-tag">{tag.rotulo && <span className="sr-only">{tag.rotulo}</span>}{tag.texto}</span>)}
            </span>
            <span className="pilha-lateral" aria-hidden="true">
              <span className="pilha-seta"><Icone nome="arrow-right" /></span>
              <span className="pilha-vertical">{item.codigo}</span>
            </span>
            <span className="sr-only">{item.acao}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
