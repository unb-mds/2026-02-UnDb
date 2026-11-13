import { nomeUnidade } from "@/lib/unidade";
import Link from "next/link";
import Icone from "./icone";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { DisciplinaDetalhe } from "@/lib/types/institucional";

/** Mesmo cartão das "Disciplinas mais avaliadas" da home: bloco superior só com o código e a unidade acadêmica como tag. */
const TONS = ["verde", "azul", "claro", "escuro"] as const;

export default function DisciplinaCatalogo({ disciplina, contexto = null, titulo: Titulo = "h2", indice }: {
  disciplina: DisciplinaDetalhe;
  contexto?: ContextoBusca | null;
  titulo?: "h2" | "h3";
  /** Posição na lista: quando informada, o bloco de cima ganha uma cor sólida (como nas "mais avaliadas"). */
  indice?: number;
}) {
  return (
    <li className="flex min-w-0">
      <Link href={comContextoBusca(`/disciplinas/${disciplina.id}`, contexto)} className="destaque w-full break-words">
        <div className="destaque-visual" data-tom={indice === undefined ? undefined : TONS[indice % TONS.length]}>
          <span className="destaque-pill"><span className="sr-only">Código da disciplina: </span>{disciplina.codigo}</span>
          <span className="destaque-notch" aria-hidden="true"><span className="destaque-arrow"><span className="inline-flex -rotate-45"><Icone nome="arrow-right" /></span></span></span>
        </div>
        <div className="flex flex-1 flex-col gap-3 px-3">
          <Titulo className="text-xl leading-tight font-semibold tracking-tight">{disciplina.nome}</Titulo>
          <div className="destaque-tags mt-auto"><span className="destaque-tag destaque-tag-unidade"><span className="sr-only">Unidade acadêmica: </span>{nomeUnidade(disciplina)}</span><span className="destaque-tag">Comparar professores</span></div>
        </div>
      </Link>
    </li>
  );
}
