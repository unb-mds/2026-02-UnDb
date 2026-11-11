import { identificadorValido } from "../identificador";
import { apiClient } from "./api-client";

export type Candidato = { identificador: string; nome: string; perfil_url: string; compativel: boolean };
export type EstadoIdentidade = "PENDENTE" | "CONFIRMADA" | "SEPARADA" | "APLICADA";
export type PendenciaIdentidade = {
  id: string; professor_id: string; nome: string; unidade: string; periodo: string;
  disciplina: string; turma: string; motivo: string; estado: EstadoIdentidade;
  candidatos: Candidato[]; identificador_destino: string | null; versao: number;
};
export type PreviaIdentidade = { colisoes: number; uniao_necessaria: boolean; bloqueada: boolean; turmas?: number; avaliacoes?: number };
export type DecisaoIdentidade = { id: string; usuario_id: string; acao: string; justificativa: string; identificador: string | null; versao: number; created_at: string };
const base = "/api/moderacao/identidades";
const opcoes = (signal?: AbortSignal) => ({ cache: "no-store" as const, signal });
const registro = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const numero = (v: unknown): v is number => typeof v === "number" && Number.isInteger(v) && v >= 0;
const identificador = (v: unknown): v is string => typeof v === "string" && /^\d{1,30}$/.test(v);
export function candidato(v: unknown): v is Candidato {
  return registro(v) && identificador(v.identificador) && typeof v.nome === "string" && typeof v.perfil_url === "string" && typeof v.compativel === "boolean";
}
export function pendencia(v: unknown): v is PendenciaIdentidade {
  return registro(v) && typeof v.id === "string" && identificadorValido(v.id)
    && typeof v.professor_id === "string" && identificadorValido(v.professor_id)
    && [v.nome, v.unidade, v.periodo, v.disciplina, v.turma, v.motivo].every(x => typeof x === "string")
    && ["PENDENTE", "CONFIRMADA", "SEPARADA", "APLICADA"].includes(String(v.estado))
    && numero(v.versao) && v.versao > 0 && Array.isArray(v.candidatos) && v.candidatos.every(candidato)
    && (v.identificador_destino === null || identificador(v.identificador_destino));
}
function caminho(id: string): string {
  if (!identificadorValido(id)) throw new Error("Pendência inválida.");
  return `${base}/${id}`;
}
export async function listarIdentidades(estado: EstadoIdentidade, offset: number, signal?: AbortSignal): Promise<PendenciaIdentidade[]> {
  const v = await apiClient.request<unknown>(base, { estado, offset: String(offset) }, opcoes(signal));
  if (!Array.isArray(v) || !v.every(pendencia)) throw new Error("Resposta de identidades incompatível.");
  return v;
}
export async function consultarPrevia(id: string, perfil: string, signal?: AbortSignal): Promise<PreviaIdentidade> {
  const v = await apiClient.request<unknown>(`${caminho(id)}/previa`, { identificador: perfil }, opcoes(signal));
  if (!registro(v) || !numero(v.colisoes) || typeof v.uniao_necessaria !== "boolean" || typeof v.bloqueada !== "boolean"
    || (v.turmas !== undefined && !numero(v.turmas)) || (v.avaliacoes !== undefined && !numero(v.avaliacoes))) throw new Error("Prévia incompatível.");
  return v as PreviaIdentidade;
}
export async function decidirIdentidade(item: PendenciaIdentidade, acao: "CONFIRMAR" | "SEPARAR", justificativa: string, perfil?: string): Promise<PendenciaIdentidade> {
  const v = await apiClient.post<unknown, object>(`${caminho(item.id)}/decisoes`, { acao, versao: item.versao, justificativa, identificador: perfil ?? null }, opcoes());
  if (!pendencia(v) || v.id !== item.id) throw new Error("Decisão incompatível.");
  return v;
}
export async function historicoIdentidade(id: string, signal?: AbortSignal): Promise<DecisaoIdentidade[]> {
  const v = await apiClient.request<unknown>(`${caminho(id)}/decisoes`, {}, opcoes(signal));
  if (!Array.isArray(v) || !v.every(x => registro(x) && typeof x.id === "string" && identificadorValido(x.id)
    && typeof x.usuario_id === "string" && identificadorValido(x.usuario_id) && typeof x.acao === "string"
    && typeof x.justificativa === "string" && numero(x.versao) && typeof x.created_at === "string"
    && (x.identificador === null || identificador(x.identificador)))) throw new Error("Histórico incompatível.");
  return v as DecisaoIdentidade[];
}
