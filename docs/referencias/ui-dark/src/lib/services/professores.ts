import { apiClient } from "./api-client";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "../types/institucional";

/** Formato exato de backend/app/schemas/institucional.py — nunca exposto fora deste arquivo. */
interface ProfessorDetalheWire {
  id: string;
  nome: string;
  departamento: string;
  siape: string | null;
  identidade_confirmada: boolean;
}

interface DisciplinaDetalheWire {
  id: string;
  codigo: string;
  nome: string;
  departamento: string;
  identificador_externo: string | null;
  creditos: number | null;
}

function paraProfessor(wire: ProfessorDetalheWire): ProfessorDetalhe {
  return {
    id: wire.id,
    nome: wire.nome,
    departamento: wire.departamento,
    siape: wire.siape,
    identidadeConfirmada: wire.identidade_confirmada,
  };
}

function paraDisciplina(wire: DisciplinaDetalheWire): DisciplinaDetalhe {
  return {
    id: wire.id,
    codigo: wire.codigo,
    nome: wire.nome,
    departamento: wire.departamento,
    identificadorExterno: wire.identificador_externo,
    creditos: wire.creditos,
  };
}

/** GET /api/professores?nome= — busca parcial, sem distinção de caixa ou acento (Issue #44). */
export async function listarProfessores(nome?: string): Promise<ProfessorDetalhe[]> {
  const wire = await apiClient.request<ProfessorDetalheWire[]>("/api/professores", { nome });
  return wire.map(paraProfessor);
}

/** GET /api/professores/{id} — lança ApiError com naoEncontrado=true em 404. */
export async function obterProfessor(id: string): Promise<ProfessorDetalhe> {
  const wire = await apiClient.request<ProfessorDetalheWire>(`/api/professores/${id}`);
  return paraProfessor(wire);
}

/** GET /api/professores/{id}/disciplinas — base da comparação entre professores (RF12). */
export async function listarDisciplinasDoProfessor(id: string): Promise<DisciplinaDetalhe[]> {
  const wire = await apiClient.request<DisciplinaDetalheWire[]>(`/api/professores/${id}/disciplinas`);
  return wire.map(paraDisciplina);
}
