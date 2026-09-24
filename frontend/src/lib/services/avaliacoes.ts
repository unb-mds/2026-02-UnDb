import { apiClient } from "./api-client";
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

interface AvaliacaoAgregadaWireBase {
  professor_id: string;
  disciplina_id: string;
  professor: ProfessorInstitucional;
  disciplina: DisciplinaInstitucional;
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
    professor: wire.professor,
    disciplina: wire.disciplina,
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
