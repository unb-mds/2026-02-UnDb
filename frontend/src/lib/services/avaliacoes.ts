import { apiClient } from "./api-client";
import { identificadorValido } from "../identificador";
import type {
  AvaliacaoAgregada,
  AvaliacaoInput,
  Dificuldade,
  QualidadeMaterial,
} from "../types/avaliacao";
import type { DisciplinaInstitucional, ProfessorInstitucional } from "../types/institucional";

/**
 * Destino implementado pela #39 no router de avaliações. A integração completa da
 * interface permanece na #116; não presumimos campos de criação/substituição.
 */
export async function enviarAvaliacao(dados: AvaliacaoInput): Promise<void> {
  await apiClient.post<unknown, AvaliacaoInput>("/api/avaliacoes", dados);
}

export async function enviarAvaliacaoComComentario(dados: AvaliacaoInput, signal?: AbortSignal): Promise<{ id: string; comentario_erro: string | null }> {
  const resposta = await apiClient.post<unknown, AvaliacaoInput>("/api/avaliacoes", dados, { signal });
  if (!resposta || typeof resposta !== "object" || !("id" in resposta) ||
      typeof resposta.id !== "string" || !identificadorValido(resposta.id) ||
      !("comentario_erro" in resposta) || (resposta.comentario_erro !== null && typeof resposta.comentario_erro !== "string")) {
    throw new Error("Resposta de avaliação incompatível com o contrato.");
  }
  return { id: resposta.id, comentario_erro: resposta.comentario_erro };
}

interface AvaliacaoAgregadaWireBase {
  professor_id: string;
  disciplina_id: string;
  professor: Omit<ProfessorInstitucional, "departamentoNome"> & { departamento_nome?: string | null };
  disciplina: Omit<DisciplinaInstitucional, "departamentoNome"> & { departamento_nome?: string | null };
  total_avaliacoes: number;
}

interface AvaliacaoAgregadaInsuficienteWire extends AvaliacaoAgregadaWireBase {
  dados_suficientes: false;
}

interface AvaliacaoAgregadaSuficienteWire extends AvaliacaoAgregadaWireBase {
  dados_suficientes: true;
  didatica: number;
  dificuldade: Dificuldade;
  chamada: boolean | "CONFLITANTE";
  disponibiliza_material: boolean | "CONFLITANTE";
  qualidade_material: QualidadeMaterial | null;
  recomenda: number;
}

/** Formato exato de backend/app/schemas/avaliacao.py — nunca exposto fora deste arquivo. */
type AvaliacaoAgregadaWire = AvaliacaoAgregadaSuficienteWire | AvaliacaoAgregadaInsuficienteWire;

function paraAvaliacaoAgregada(wire: AvaliacaoAgregadaWire): AvaliacaoAgregada {
  const base = {
    professorId: wire.professor_id,
    disciplinaId: wire.disciplina_id,
    professor: {
      id: wire.professor.id,
      nome: wire.professor.nome,
      departamento: wire.professor.departamento,
      departamentoNome: wire.professor.departamento_nome ?? null,
    },
    disciplina: {
      id: wire.disciplina.id,
      codigo: wire.disciplina.codigo,
      nome: wire.disciplina.nome,
      departamento: wire.disciplina.departamento,
      departamentoNome: wire.disciplina.departamento_nome ?? null,
    },
    totalAvaliacoes: wire.total_avaliacoes,
  };

  if (!wire.dados_suficientes) {
    return { ...base, dadosSuficientes: false };
  }

  return {
    ...base,
    dadosSuficientes: true,
    didatica: wire.didatica,
    dificuldade: wire.dificuldade,
    chamada: wire.chamada,
    disponibilizaMaterial: wire.disponibiliza_material,
    qualidadeMaterial: wire.qualidade_material,
    recomenda: wire.recomenda,
  };
}

/**
 * GET /api/professores/{professorId}/disciplinas/{disciplinaId} — Issue #43.
 * Lança ApiError com naoEncontrado=true quando o professor não tem vínculo
 * com a disciplina (404).
 */
export async function consultarAvaliacaoAgregada(
  professorId: string,
  disciplinaId: string,
): Promise<AvaliacaoAgregada> {
  const wire = await apiClient.request<AvaliacaoAgregadaWire>(
    `/api/professores/${professorId}/disciplinas/${disciplinaId}`,
  );
  return paraAvaliacaoAgregada(wire);
}
