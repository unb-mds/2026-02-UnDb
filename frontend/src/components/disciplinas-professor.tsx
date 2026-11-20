import { nomeUnidade } from "@/lib/unidade";
import Link from "next/link";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";

export default function DisciplinasProfessor({ professorId, disciplinas, contexto = null, compacta = false }: {
  professorId: string;
  disciplinas: DisciplinaDetalhe[];
  contexto?: ContextoBusca | null;
  compacta?: boolean;
}) {
  if (!disciplinas.length) return <p className="mt-2 text-sm text-(--muted)">Nenhuma turma ativa registrada para este professor no momento.</p>;

  const limite = compacta ? 2 : 6;
  const restantes = disciplinas.slice(limite);
  const cartao = (disciplina: DisciplinaDetalhe) => (
    <li key={disciplina.id} className={`flex min-w-0 flex-col justify-between gap-3 rounded-xl border border-(--border) bg-(--raised)/80 p-3 break-words sm:gap-4 sm:p-4 ${compacta ? "" : "lg:flex-row lg:items-center"}`}>
      <div className="min-w-0">
        <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}`, contexto)} className="block hover:text-accent">
          <span className="block text-sm font-semibold sm:text-base">{disciplina.nome}</span>
          <span className="mt-1 block text-xs text-(--muted) sm:text-sm">Código da disciplina: <span className="font-mono">{disciplina.codigo}</span></span>
          <span className="mt-1 block text-xs text-(--muted) sm:text-sm">Unidade acadêmica: {nomeUnidade(disciplina)}</span>
        </Link>
      </div>
      <div className={`flex shrink-0 flex-wrap gap-2 text-sm sm:gap-3 ${compacta ? "" : "lg:max-w-64"}`}>
        <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}`, contexto)} className="button">Consultar</Link>
        <Link href={comContextoBusca(`/professores/${professorId}/disciplinas/${disciplina.id}/avaliar`, contexto)} className="button primary">Avaliar</Link>
        <Link href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)} className="link flex min-h-11 w-full items-center text-sm">Comparar professores desta disciplina →</Link>
      </div>
    </li>
  );

  return <>
    <ul className="mt-3 flex min-w-0 flex-col gap-2 sm:mt-4 sm:gap-3">{disciplinas.slice(0, limite).map(cartao)}</ul>
    {restantes.length > 0 && <details className="mt-3 min-w-0 rounded-xl border border-(--border) p-3 sm:p-4">
      <summary className="flex min-h-11 cursor-pointer items-center text-sm font-medium text-accent">Ver mais {restantes.length} {restantes.length === 1 ? "disciplina" : "disciplinas"}</summary>
      <ul className="mt-3 flex min-w-0 flex-col gap-2 sm:gap-3">{restantes.map(cartao)}</ul>
    </details>}
  </>;
}
