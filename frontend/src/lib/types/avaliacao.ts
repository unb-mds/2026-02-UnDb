import type { DisciplinaInstitucional, ProfessorInstitucional } from "./institucional";

/** Espelha backend/app/schemas/avaliacao.py — contrato da Issue #40/#25. */

export type Dificuldade = "FACIL" | "MEDIO" | "DIFICIL";
export type QualidadeMaterial = "RUIM" | "MEDIO" | "BOM";

/** Entrada individual de AvaliacaoCreate; a identidade vem exclusivamente da sessão. */
export type AvaliacaoInput = {
  professor_id: string;
  disciplina_id: string;
  didatica: number;
  dificuldade: Dificuldade;
  chamada: boolean;
  recomenda: boolean;
} & (
  | { disponibiliza_material: false; qualidade_material: null }
  | { disponibiliza_material: true; qualidade_material: QualidadeMaterial }
);

interface AvaliacaoAgregadaBase {
  professorId: string;
  disciplinaId: string;
  professor: ProfessorInstitucional;
  disciplina: DisciplinaInstitucional;
  totalAvaliacoes: number;
}

export interface AvaliacaoAgregadaInsuficiente extends AvaliacaoAgregadaBase {
  dadosSuficientes: false;
}

export interface AvaliacaoAgregadaSuficiente extends AvaliacaoAgregadaBase {
  dadosSuficientes: true;
  didatica: number;
  dificuldade: Dificuldade;
  chamada: boolean | "CONFLITANTE";
  disponibilizaMaterial: boolean | "CONFLITANTE";
  qualidadeMaterial: QualidadeMaterial | null;
  /** Percentual inteiro, 0–100 — única chave de ordenação válida (RF13). */
  recomenda: number;
}

export type AvaliacaoAgregada = AvaliacaoAgregadaSuficiente | AvaliacaoAgregadaInsuficiente;

export interface ComparacaoProfessores {
  disciplina: DisciplinaInstitucional;
  professores: AvaliacaoAgregada[];
}
