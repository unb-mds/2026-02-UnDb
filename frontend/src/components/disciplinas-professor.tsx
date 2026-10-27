import Link from "next/link";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";

export default function DisciplinasProfessor({ professorId, disciplinas }: {
  professorId: string;
  disciplinas: DisciplinaDetalhe[];
}) {
  if (disciplinas.length === 0) {
    return (
      <p className="mt-2 text-sm text-foreground/60">
        Nenhuma turma ativa registrada para este professor no momento.
      </p>
    );
  }

  return (
    <ul className="mt-2 flex min-w-0 flex-col gap-2">
      {disciplinas.map((disciplina) => (
        <li key={disciplina.id} className="min-w-0 rounded-lg border border-foreground/10 px-4 py-3 break-words">
          <Link href={`/professores/${professorId}/disciplinas/${disciplina.id}`} className="block hover:text-accent">
            <span className="block font-medium">{disciplina.nome}</span>
            <span className="mt-1 block text-sm text-foreground/70">
              Código da disciplina: <span className="font-mono">{disciplina.codigo}</span>
            </span>
            <span className="mt-1 block text-xs text-foreground/60">Unidade acadêmica: {disciplina.departamento}</span>
          </Link>
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm">
            <Link
              href={`/disciplinas/${disciplina.id}`}
              className="text-accent underline underline-offset-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Comparar professores desta disciplina →
            </Link>
            <Link
              href={`/professores/${professorId}/disciplinas/${disciplina.id}/avaliar`}
              className="font-medium text-accent underline underline-offset-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Avaliar
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}
