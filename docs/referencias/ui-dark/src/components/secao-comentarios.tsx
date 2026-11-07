import type { ComentarioPublico } from "@/lib/types/comentario";
import ItemComentario from "./item-comentario";

type SecaoComentariosProps = {
  comentarios: ComentarioPublico[];
};

export default function SecaoComentarios({ comentarios }: SecaoComentariosProps) {
  return (
    <section aria-labelledby="titulo-comentarios" className="flex flex-col gap-4 border-t border-foreground/10 pt-6">
      <div className="flex items-baseline justify-between">
        <h2 id="titulo-comentarios" className="text-lg font-semibold">
          Comentários
        </h2>
        <span className="text-xs text-foreground/60">
          {comentarios.length === 0
            ? "Nenhum comentário"
            : `${comentarios.length} ${comentarios.length === 1 ? "comentário publicado" : "comentários publicados"}`}
        </span>
      </div>

      {comentarios.length === 0 ? (
        <p className="text-sm text-foreground/70">
          Ainda não há comentários publicados para este professor nesta disciplina.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {comentarios.map((comentario) => (
            <ItemComentario key={comentario.id} comentario={comentario} />
          ))}
        </div>
      )}
    </section>
  );
}
