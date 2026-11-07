import type { ComentarioDoAutor, EstadoComentario } from "./types/comentario";

export const rotulosEstadoComentario: Record<EstadoComentario, string> = {
  PENDENTE: "Em análise",
  PUBLICADO: "Publicado",
  SUSPENSO: "Temporariamente indisponível",
  REMOVIDO: "Removido",
  RETIRADO: "Retirado",
  SUBSTITUIDO: "Substituído",
  REJEITADO: "Rejeitado",
};

// RF20/R2-DEC-05: uma versão pendente, inclusive substituta, não é pública.
export function descricaoEstadoComentario(comentario: ComentarioDoAutor): string {
  switch (comentario.estado) {
    case "PENDENTE":
      return comentario.substitui_id
        ? "Seu substituto aguarda aprovação. O envio não publica nem restaura a versão anterior; confira o estado dela abaixo."
        : "Seu comentário aguarda aprovação humana e ainda não está público.";
    case "PUBLICADO":
      return "Este comentário está visível publicamente sem identificar sua autoria.";
    case "SUSPENSO":
      return "Este comentário não está visível publicamente enquanto aguarda análise.";
    case "REMOVIDO":
      return "Este comentário foi removido e não está visível publicamente.";
    case "RETIRADO":
      return "Você retirou este comentário; ele não está visível publicamente.";
    case "REJEITADO":
      return "Este texto foi rejeitado, não está visível publicamente e seu conteúdo foi descartado.";
    case "SUBSTITUIDO":
      return "Este texto foi substituído e não está mais visível publicamente.";
  }
}

// RF20/R2-DEC-15: texto descartado pode ser nulo e não representa conteúdo público.
export function textoExibivelComentario(comentario: ComentarioDoAutor): string {
  return comentario.texto ?? "O texto desta versão não está mais disponível.";
}
