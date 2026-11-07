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
      className="flex flex-col gap-3 rounded-xl border border-foreground/10 bg-background p-4 transition"
    >
      <div className="flex items-center justify-between gap-4">
        <span className="text-xs text-foreground/60">Publicado em {dataFormatada}</span>
        <button
          type="button"
          onClick={() => setModalAberto(true)}
          aria-label={`Denunciar comentário`}
          data-testid={`botao-denunciar-${comentario.id}`}
          className="text-xs font-medium text-red-600 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 dark:text-red-400"
        >
          Denunciar
        </button>
      </div>

      <p className="text-sm whitespace-pre-wrap text-foreground/90 leading-relaxed">
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
