import { apiClient } from "./api-client";
import type { DisciplinaDetalhe, TurmaInstitucional } from "../types/institucional";

/** Formato exato de backend/app/schemas/institucional.py — nunca exposto fora deste arquivo. */
interface DisciplinaDetalheWire {
  id: string;
  codigo: string;
  nome: string;
  departamento: string;
  identificador_externo: string | null;
  creditos: number | null;
}

interface ProfessorDetalheWire {
  id: string;
  nome: string;
  departamento: string;
  siape: string | null;
  identidade_confirmada: boolean;
}

interface TurmaInstitucionalWire {
  id: string;
  fonte: string;
  codigo: string;
  semestre: string;
  ativa: boolean;
  professores: ProfessorDetalheWire[];
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

function paraTurma(wire: TurmaInstitucionalWire): TurmaInstitucional {
  return {
    id: wire.id,
    fonte: wire.fonte,
    codigo: wire.codigo,
    semestre: wire.semestre,
    ativa: wire.ativa,
    professores: wire.professores.map((professor) => ({
      id: professor.id,
      nome: professor.nome,
      departamento: professor.departamento,
      siape: professor.siape,
      identidadeConfirmada: professor.identidade_confirmada,
    })),
  };
}

/** GET /api/disciplinas?codigo=&nome= — busca por código exato/parcial ou nome parcial (Issue #45). */
export async function listarDisciplinas(params: { codigo?: string; nome?: string } = {}): Promise<DisciplinaDetalhe[]> {
  const wire = await apiClient.request<DisciplinaDetalheWire[]>("/api/disciplinas", params);
  return wire.map(paraDisciplina);
}

/**
 * Busca por um único termo que pode ser nome parcial ou código (Issue #45).
 * O backend trata `codigo` e `nome` como filtros combinados por E — para aceitar
 * qualquer um dos dois a partir de um só campo, consulta os dois em paralelo e
 * mescla o resultado, sem repetir disciplina.
 */
export async function buscarDisciplinas(termo: string): Promise<DisciplinaDetalhe[]> {
  const [porCodigo, porNome] = await Promise.all([
    listarDisciplinas({ codigo: termo }),
    listarDisciplinas({ nome: termo }),
  ]);

  const porId = new Map<string, DisciplinaDetalhe>();
  for (const disciplina of [...porCodigo, ...porNome]) {
    porId.set(disciplina.id, disciplina);
  }
  return Array.from(porId.values());
}

/** GET /api/disciplinas/{id} — lança ApiError com naoEncontrado=true em 404. */
export async function obterDisciplina(id: string): Promise<DisciplinaDetalhe> {
  const wire = await apiClient.request<DisciplinaDetalheWire>(`/api/disciplinas/${id}`);
  return paraDisciplina(wire);
}

/** GET /api/disciplinas/{id}/turmas — turmas ativas com seus docentes (zero, um ou vários). */
export async function listarTurmasDaDisciplina(id: string): Promise<TurmaInstitucional[]> {
  const wire = await apiClient.request<TurmaInstitucionalWire[]>(`/api/disciplinas/${id}/turmas`);
  return wire.map(paraTurma);
}
