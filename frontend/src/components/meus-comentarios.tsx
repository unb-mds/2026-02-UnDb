import {
  descricaoEstadoComentario,
  rotulosEstadoComentario,
  textoExibivelComentario,
} from "@/lib/apresentacao-comentario";
import type { ComentarioDoAutor } from "@/lib/types/comentario";

type MeusComentariosProps = {
  comentarios: ComentarioDoAutor[];
};

export default function MeusComentarios({ comentarios }: MeusComentariosProps) {
  if (comentarios.length === 0) {
    return (
      <p className="text-sm text-foreground/70">
        Você ainda não possui comentários para acompanhar.
      </p>
    );
  }

  return (
    <section aria-labelledby="titulo-meus-comentarios" className="flex flex-col gap-3">
      <div>
        <h2 id="titulo-meus-comentarios" className="text-lg font-semibold">
          Meus comentários
        </h2>
        <p className="text-sm text-foreground/70">
          Acompanhe o estado de cada versão sem expor sua autoria publicamente.
        </p>
      </div>
      <ul className="flex flex-col gap-3">
        {comentarios.map((comentario) => (
          <li
            key={comentario.id}
            data-testid={`meu-comentario-${comentario.id}`}
            className="rounded-xl border border-foreground/10 bg-background p-4"
          >
            <p className="text-sm font-medium text-accent">{rotulosEstadoComentario[comentario.estado]}</p>
            <p className="mt-1 text-sm text-foreground/70">{descricaoEstadoComentario(comentario)}</p>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
              {textoExibivelComentario(comentario)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
