import { nomeUnidade } from "@/lib/unidade";
import Link from "next/link";
import Icone from "./icone";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";

export default function DisciplinaCatalogo({ disciplina, contexto = null, titulo: Titulo = "h2" }: {
  disciplina: DisciplinaDetalhe;
  contexto?: ContextoBusca | null;
  titulo?: "h2" | "h3";
}) {
  return (
    <li className="min-w-0">
      <Link href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)} className="tile flex h-full flex-col items-start gap-3 p-5 break-words">
        <span className="code-chip"><span className="sr-only">Código da disciplina: </span>{disciplina.codigo}</span>
        <Titulo className="text-lg leading-snug font-semibold">{disciplina.nome}</Titulo>
        <p className="text-sm text-(--ink-soft)">Unidade acadêmica: {nomeUnidade(disciplina)}</p>
        <span className="mt-auto inline-flex items-center gap-2 pt-2 text-sm font-medium text-accent">Comparar professores <Icone nome="arrow-right" pequeno /></span>
      </Link>
    </li>
  );
}
