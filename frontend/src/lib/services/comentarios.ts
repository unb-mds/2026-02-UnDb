import { identificadorValido } from "../identificador";
import type { ComentarioPublico } from "../types/comentario";
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

  return resposta;
}
