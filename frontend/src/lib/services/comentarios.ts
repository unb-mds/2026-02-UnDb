import { identificadorValido } from "../identificador";
import type {
  ComentarioDoAutor,
  ComentarioPublico,
  EstadoComentario,
} from "../types/comentario";
import { ESTADOS_COMENTARIO } from "../types/comentario";
import { apiClient } from "./api-client";

const registro = (valor: unknown): valor is Record<string, unknown> =>
  typeof valor === "object" && valor !== null && !Array.isArray(valor);

const idValido = (valor: unknown): valor is string =>
  typeof valor === "string" && identificadorValido(valor);

function comentarioPublico(valor: unknown): valor is ComentarioPublico {
  return (
    registro(valor) &&
    idValido(valor.id) &&
    typeof valor.texto === "string" &&
    typeof valor.created_at === "string"
  );
}

export async function listarComentariosPublicados(
  professorId: string,
  disciplinaId: string,
  signal?: AbortSignal,
): Promise<ComentarioPublico[]> {
  if (!identificadorValido(professorId) || !identificadorValido(disciplinaId)) {
    throw new Error("Identificadores inválidos para consulta de comentários.");
  }

  const resposta = await apiClient.request<unknown>(
    `/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`,
    {},
    { signal },
  );

  if (!Array.isArray(resposta) || !resposta.every(comentarioPublico)) {
    throw new Error("Resposta de comentários incompatível com o contrato.");
  }

  return resposta.map(({ id, texto, created_at }) => ({ id, texto, created_at }));
}

function comentarioDoAutor(valor: unknown): valor is ComentarioDoAutor {
  return (
    registro(valor) &&
    idValido(valor.id) &&
    (valor.texto === null || typeof valor.texto === "string") &&
    typeof valor.created_at === "string" &&
    typeof valor.updated_at === "string" &&
    typeof valor.estado === "string" &&
    ESTADOS_COMENTARIO.includes(valor.estado as EstadoComentario) &&
    idValido(valor.avaliacao_id) &&
    (valor.substitui_id === null || idValido(valor.substitui_id))
  );
}

export async function consultarMeusComentarios(signal?: AbortSignal, contexto?: { professorId: string; disciplinaId: string }): Promise<ComentarioDoAutor[]> {
  if (contexto && (!identificadorValido(contexto.professorId) || !identificadorValido(contexto.disciplinaId))) {
    throw new Error("Contexto de comentários inválido.");
  }
  const query = contexto ? { professor_id: contexto.professorId, disciplina_id: contexto.disciplinaId } : {};
  const resposta = await apiClient.request<unknown>("/api/comentarios/meu", query, { cache: "no-store", signal });
  if (!Array.isArray(resposta) || !resposta.every(comentarioDoAutor)) {
    throw new Error("Resposta de comentários do autor incompatível com o contrato.");
  }
  return resposta.map(
    ({ id, texto, created_at, updated_at, estado, avaliacao_id, substitui_id }) => ({
      id,
      texto,
      created_at,
      updated_at,
      estado,
      avaliacao_id,
      substitui_id,
    }),
  );
}

export async function retirarComentario(id: string, signal?: AbortSignal): Promise<ComentarioDoAutor> {
  if (!identificadorValido(id)) throw new Error("Identificador de comentário inválido.");
  const resposta = await apiClient.patch<unknown>(`/api/comentarios/${id}/retirar`, { signal });
  if (!comentarioDoAutor(resposta) || resposta.id !== id || resposta.estado !== "RETIRADO") {
    throw new Error("Resposta de retirada incompatível com o contrato.");
  }
  const { texto, created_at, updated_at, estado, avaliacao_id, substitui_id } = resposta;
  return { id, texto, created_at, updated_at, estado, avaliacao_id, substitui_id };
}
