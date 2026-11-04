import type { ComentarioDoAutor, EstadoComentario } from "@/lib/types/comentario";

type MeusComentariosProps = {
  comentarios: ComentarioDoAutor[];
};

const rotulos: Record<EstadoComentario, string> = {
  PENDENTE: "Em análise",
  PUBLICADO: "Publicado",
  SUSPENSO: "Temporariamente indisponível",
  REMOVIDO: "Removido",
  RETIRADO: "Retirado",
  SUBSTITUIDO: "Substituído",
};

function descricao(comentario: ComentarioDoAutor): string {
  switch (comentario.estado) {
    case "PENDENTE":
      return comentario.substitui_id
        ? "Seu substituto aguarda aprovação. O texto aprovado anterior continua público enquanto estiver disponível."
        : "Seu comentário aguarda aprovação humana e ainda não está público.";
    case "PUBLICADO":
      return "Este comentário está visível publicamente sem identificar sua autoria.";
    case "SUSPENSO":
      return "Este comentário não está visível publicamente enquanto aguarda análise.";
    case "REMOVIDO":
      return "Este comentário foi removido e não está visível publicamente.";
    case "RETIRADO":
      return "Você retirou este comentário; ele não está visível publicamente.";
    case "SUBSTITUIDO":
      return "Este texto foi substituído e não está mais visível publicamente.";
  }
}

function textoExibivel(comentario: ComentarioDoAutor): string {
  return comentario.texto ?? "O texto desta versão não está mais disponível.";
}

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
            <p className="text-sm font-medium text-accent">{rotulos[comentario.estado]}</p>
            <p className="mt-1 text-sm text-foreground/70">{descricao(comentario)}</p>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
              {textoExibivel(comentario)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
