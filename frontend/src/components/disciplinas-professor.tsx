import { nomeUnidade } from "@/lib/unidade";
import Link from "next/link";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";

export default function DisciplinasProfessor({ professorId, disciplinas, contexto = null }: {
  professorId: string;
  disciplinas: DisciplinaDetalhe[];
  contexto?: ContextoBusca | null;
}) {
  if (disciplinas.length === 0) {
    return (
      <p className="mt-2 text-sm text-(--muted)">
        Nenhuma turma ativa registrada para este professor no momento.
      </p>
    );
  }

  return (
    <ul className="mt-4 flex min-w-0 flex-col gap-3">
      {disciplinas.map((disciplina) => (
        <li key={disciplina.id} className="flex min-w-0 flex-col justify-between gap-4 rounded-xl border border-(--border) bg-(--raised)/80 p-4 break-words lg:flex-row lg:items-center">
          <div className="min-w-0">
            <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}`, contexto)} className="block hover:text-accent">
              <span className="block text-base font-semibold">{disciplina.nome}</span>
              <span className="mt-1 block text-sm text-(--muted)">
                Código da disciplina: <span className="font-mono">{disciplina.codigo}</span>
              </span>
              <span className="mt-1 block text-sm text-(--muted)">Unidade acadêmica: {nomeUnidade(disciplina)}</span>
            </Link>
          </div>
          <div className="flex shrink-0 flex-wrap gap-3 text-sm lg:max-w-64">
            <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}`, contexto)} className="button">Consultar</Link>
            <Link
              href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}/avaliar`, contexto)}
              className="button primary"
            >
              Avaliar
            </Link>
            <Link
              href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)}
              className="link w-full text-sm"
            >
              Comparar professores desta disciplina →
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}
