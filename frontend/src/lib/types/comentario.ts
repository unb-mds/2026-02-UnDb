export type ComentarioPublico = {
  id: string;
  texto: string;
  created_at: string;
};

/**
 * Estados de uma versão de comentário (RF20, R2-DEC-04/05).
 * Reutiliza os mesmos valores do backend (`EstadoComentario`); não cria enum paralelo.
 */
export type EstadoComentario =
  | "PENDENTE"
  | "PUBLICADO"
  | "SUSPENSO"
  | "REMOVIDO"
  | "RETIRADO"
  | "SUBSTITUIDO";

export const ESTADOS_COMENTARIO: EstadoComentario[] = [
  "PENDENTE",
  "PUBLICADO",
  "SUSPENSO",
  "REMOVIDO",
  "RETIRADO",
  "SUBSTITUIDO",
];

/**
 * Versão de comentário visível ao próprio autor (GET /api/comentarios/meu).
 * Espelha backend/app/schemas/comentario.py (ComentarioDoAuthorResponse).
 * `texto` admite `null`: descarte/retirada do autor remove o texto sem remover o registro da versão.
 * O autor acompanha a distinção entre versão publicada (PUBLICADO) e substituto em revisão (PENDENTE).
 */
export type ComentarioDoAutor = {
  id: string;
  texto: string | null;
  created_at: string;
  updated_at: string;
  estado: EstadoComentario;
  avaliacao_id: string;
  substitui_id: string | null;
};
