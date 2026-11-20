import { apiClient } from "./api-client";
import { identificadorValido } from "../identificador";

export type DisciplinaDestaque = {
  id: string; codigo: string; nome: string; departamento: string;
  departamentoNome?: string | null; total_avaliacoes: number;
};

export async function listarDestaques(signal?: AbortSignal): Promise<DisciplinaDestaque[]> {
  const resposta = await apiClient.request<unknown>("/api/disciplinas/destaques", {}, { signal });
  if (!Array.isArray(resposta)) throw new Error("Resposta de destaques inválida.");
  return resposta.slice(0, 6).map((d: unknown) => {
    if (!d || typeof d !== "object" || !("id" in d) || typeof d.id !== "string" || !identificadorValido(d.id) ||
        !("nome" in d) || typeof d.nome !== "string" || !("codigo" in d) || typeof d.codigo !== "string" ||
        !("departamento" in d) || typeof d.departamento !== "string" ||
        !("total_avaliacoes" in d) || typeof d.total_avaliacoes !== "number" || !Number.isSafeInteger(d.total_avaliacoes) || d.total_avaliacoes < 1) throw new Error("Disciplina de destaque inválida.");
    return { id: d.id, nome: d.nome, codigo: d.codigo, departamento: d.departamento, total_avaliacoes: d.total_avaliacoes,
      departamentoNome: "departamento_nome" in d && typeof d.departamento_nome === "string" ? d.departamento_nome : null };
  });
}
