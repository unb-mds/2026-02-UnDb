import type { DisciplinaInstitucional, ProfessorInstitucional } from "./institucional";

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
  dificuldade: "FACIL" | "MEDIO" | "DIFICIL";
  chamada: boolean | "CONFLITANTE";
  disponibilizaMaterial: boolean | "CONFLITANTE";
  qualidadeMaterial: "RUIM" | "MEDIO" | "BOM" | null;
  recomenda: number;
}

export type AvaliacaoAgregada = AvaliacaoAgregadaSuficiente | AvaliacaoAgregadaInsuficiente;

export interface ComparacaoProfessores {
  disciplina: DisciplinaInstitucional;
  professores: AvaliacaoAgregada[];
}
