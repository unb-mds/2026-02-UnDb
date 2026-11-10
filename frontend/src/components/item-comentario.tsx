"use client";

import { useState } from "react";
import type { ComentarioPublico } from "@/lib/types/comentario";
import ModalDenuncia from "./modal-denuncia";

type ItemComentarioProps = {
  comentario: ComentarioPublico;
};

export default function ItemComentario({ comentario }: ItemComentarioProps) {
  const [modalAberto, setModalAberto] = useState(false);

  const dataFormatada = new Date(comentario.created_at).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  return (
    <article
      data-testid={`comentario-${comentario.id}`}
      className="flex min-w-0 flex-col gap-3 rounded-xl border border-foreground/10 bg-background p-4 transition-colors hover:border-foreground/20"
    >
      <div className="flex items-center justify-between gap-4">
        <span className="text-xs text-foreground/60">Publicado em {dataFormatada}</span>
        <button
          type="button"
          onClick={() => setModalAberto(true)}
          aria-label={`Denunciar comentário publicado em ${dataFormatada}`}
          data-testid={`botao-denunciar-${comentario.id}`}
          className="inline-flex min-h-11 items-center justify-center rounded-lg border border-red-400/50 px-3 text-xs font-semibold text-red-600 transition-colors hover:border-red-400 hover:bg-red-500/10 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-400 dark:text-red-400"
        >
          Denunciar
        </button>
      </div>

      <p className="break-words text-sm leading-relaxed whitespace-pre-wrap text-foreground/90">
        {comentario.texto}
      </p>

      <ModalDenuncia
        versaoId={comentario.id}
        aberto={modalAberto}
        aoFechar={() => setModalAberto(false)}
      />
    </article>
  );
}
