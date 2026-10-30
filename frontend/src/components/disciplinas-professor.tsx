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
      <p className="mt-2 text-sm text-foreground/60">
        Nenhuma turma ativa registrada para este professor no momento.
      </p>
    );
  }

  return (
    <ul className="mt-4 flex min-w-0 flex-col gap-3">
      {disciplinas.map((disciplina) => (
        <li key={disciplina.id} className="min-w-0 rounded-lg bg-foreground/[0.03] p-4 break-words">
          <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}`, contexto)} className="block hover:text-accent">
            <span className="block text-lg font-semibold">{disciplina.nome}</span>
            <span className="mt-1 block text-sm text-foreground/70">
              Código da disciplina: <span className="font-mono">{disciplina.codigo}</span>
            </span>
            <span className="mt-1 block text-sm text-foreground/70">Unidade acadêmica: {disciplina.departamento}</span>
          </Link>
          <div className="mt-3 flex flex-wrap gap-3 text-sm">
            <Link
              href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}/avaliar`, contexto)}
              className="rounded-lg bg-accent px-4 py-2.5 text-center font-medium text-on-accent hover:opacity-90"
            >
              Avaliar nesta disciplina →
            </Link>
            <Link
              href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)}
              className="rounded-lg border border-accent/30 px-4 py-2.5 text-center font-medium text-accent hover:bg-accent/5"
            >
              Comparar professores desta disciplina →
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}
