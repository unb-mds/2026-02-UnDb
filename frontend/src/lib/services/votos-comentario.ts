import { identificadorValido } from "../identificador";
import type { UtilidadeComentario, VotoComentario } from "../types/comentario";
import { apiClient } from "./api-client";

function validar(valor: unknown): UtilidadeComentario {
  if (typeof valor !== "object" || valor === null) throw new Error("Resposta de utilidade inválida.");
  const v = valor as Record<string, unknown>;
  if (!Number.isSafeInteger(v.uteis) || (v.uteis as number) < 0 ||
      !Number.isSafeInteger(v.nao_uteis) || (v.nao_uteis as number) < 0 ||
      ![null, "UTIL", "NAO_UTIL"].includes(v.meu_voto as VotoComentario | null)) {
    throw new Error("Resposta de utilidade inválida.");
  }
  return { uteis: v.uteis as number, nao_uteis: v.nao_uteis as number, meu_voto: v.meu_voto as VotoComentario | null };
}

function caminho(id: string): string {
  if (!identificadorValido(id)) throw new Error("Comentário inválido.");
  return `/api/comentarios/${id}`;
}

export async function consultarUtilidade(id: string, signal?: AbortSignal): Promise<UtilidadeComentario> {
  return validar(await apiClient.request<unknown>(`${caminho(id)}/utilidade`, {}, { cache: "no-store", signal }));
}

export async function definirVoto(id: string, voto: VotoComentario | null, signal?: AbortSignal): Promise<UtilidadeComentario> {
  return validar(await apiClient.post<unknown, { voto: VotoComentario | null }>(`${caminho(id)}/voto`, { voto }, { cache: "no-store", signal }));
}
