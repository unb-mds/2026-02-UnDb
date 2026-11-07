export type ComentarioPublico = {
  id: string;
  texto: string;
  created_at: string;
};

// Estados compartilhados com o contrato privado existente da PR #192.
import { estadosComentario, type EstadoComentario } from "./moderacao";
export type { EstadoComentario };
export const ESTADOS_COMENTARIO = estadosComentario;

/**
 * Versão de comentário visível ao próprio autor (GET /api/comentarios/meu).
 * Espelha backend/app/schemas/comentario.py (ComentarioDoAutorResponse).
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
