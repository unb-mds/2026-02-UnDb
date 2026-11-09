import Link from "next/link";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";

export default function DisciplinaCatalogo({ disciplina, contexto = null, titulo: Titulo = "h2" }: {
  disciplina: DisciplinaDetalhe;
  contexto?: ContextoBusca | null;
  titulo?: "h2" | "h3";
}) {
  return (
    <li className="min-w-0">
      <Link href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)} className="flex h-full flex-col items-start gap-3 rounded-2xl border border-(--border) bg-(--panel) p-5 break-words transition hover:border-accent/60">
        <span className="rounded-md bg-(--primary)/15 px-2 py-1 text-xs text-accent">Código da disciplina: <span className="font-mono">{disciplina.codigo}</span></span>
        <Titulo className="text-lg leading-snug font-semibold">{disciplina.nome}</Titulo>
        <p className="text-sm text-(--muted)">Unidade acadêmica: {disciplina.departamento}</p>
        <span className="mt-auto pt-2 text-sm font-medium text-accent">Comparar professores →</span>
      </Link>
    </li>
  );
}
