import { identificadorValido } from "../identificador";
import { apiClient } from "./api-client";
import type { Dificuldade, QualidadeMaterial } from "../types/avaliacao";

export type MinhaAvaliacao = {
  id: string; professor_id: string; disciplina_id: string;
  professor: { nome: string }; disciplina: { nome: string; codigo: string };
  didatica: number; dificuldade: Dificuldade; chamada: boolean;
  disponibiliza_material: boolean; qualidade_material: QualidadeMaterial | null;
  recomenda: boolean; updated_at: string;
};
export type MinhasAvaliacoes = { itens: MinhaAvaliacao[]; total: number; pagina: number; tamanho: number };

function objeto(valor: unknown): valor is Record<string, unknown> {
  return valor !== null && typeof valor === "object";
}

function avaliacaoValida(valor: unknown): valor is MinhaAvaliacao {
  if (!objeto(valor)) return false;
  return [valor.id, valor.professor_id, valor.disciplina_id].every(id => typeof id === "string" && identificadorValido(id)) &&
    objeto(valor.professor) && typeof valor.professor.nome === "string" &&
    objeto(valor.disciplina) && typeof valor.disciplina.nome === "string" && typeof valor.disciplina.codigo === "string" &&
    typeof valor.didatica === "number" && Number.isInteger(valor.didatica) && valor.didatica >= 1 && valor.didatica <= 5 &&
    (valor.dificuldade === "FACIL" || valor.dificuldade === "MEDIO" || valor.dificuldade === "DIFICIL") &&
    typeof valor.chamada === "boolean" && typeof valor.recomenda === "boolean" &&
    typeof valor.disponibiliza_material === "boolean" &&
    (valor.disponibiliza_material ? valor.qualidade_material === "RUIM" || valor.qualidade_material === "MEDIO" || valor.qualidade_material === "BOM" : valor.qualidade_material === null) &&
    typeof valor.updated_at === "string" && Number.isFinite(Date.parse(valor.updated_at));
}

export async function consultarMinhasAvaliacoes(pagina: number, signal?: AbortSignal): Promise<MinhasAvaliacoes> {
  if (!Number.isSafeInteger(pagina) || pagina < 1 || pagina > 100000) throw new Error("Página inválida.");
  const resposta = await apiClient.request<unknown>("/api/avaliacoes/minhas", { pagina: String(pagina) }, { cache: "no-store", signal });
  if (!objeto(resposta) || !Array.isArray(resposta.itens) || !resposta.itens.every(avaliacaoValida) ||
      typeof resposta.total !== "number" || !Number.isSafeInteger(resposta.total) || resposta.total < 0 ||
      resposta.pagina !== pagina || resposta.tamanho !== 10 || resposta.itens.length > 10 || resposta.itens.length > resposta.total) {
    throw new Error("Resposta de avaliações incompatível com o contrato.");
  }
  return { itens: resposta.itens, total: resposta.total, pagina, tamanho: resposta.tamanho };
}
