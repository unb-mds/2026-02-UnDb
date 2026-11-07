/**
 * Espelha backend/app/schemas/institucional.py (contrato entregue pela Issue #25).
 * Endpoints fonte: GET /api/professores* e GET /api/disciplinas* — ver specs.md §8.
 */

export interface ProfessorInstitucional {
  id: string;
  nome: string;
  departamento: string;
}

export interface ProfessorDetalhe extends ProfessorInstitucional {
  siape: string | null;
  identidadeConfirmada: boolean;
}

export interface DisciplinaInstitucional {
  id: string;
  codigo: string;
  nome: string;
  departamento: string;
}

export interface DisciplinaDetalhe extends DisciplinaInstitucional {
  identificadorExterno: string | null;
  creditos: number | null;
}

export interface TurmaInstitucional {
  id: string;
  fonte: string;
  codigo: string;
  semestre: string;
  ativa: boolean;
  professores: ProfessorDetalhe[];
}
