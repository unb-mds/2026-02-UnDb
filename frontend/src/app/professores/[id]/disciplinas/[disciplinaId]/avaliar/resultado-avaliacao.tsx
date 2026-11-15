import Link from "next/link";
import Icone from "@/components/icone";
import IconeResultado from "@/components/icone-resultado";

export type ContextoResultado = {
  professor: string;
  disciplina: string;
  codigo: string;
  resultadosHref: string;
};

export default function ResultadoAvaliacao({ contexto, avisoComentario, aoRevisar }: {
  contexto: ContextoResultado;
  avisoComentario: string | null;
  aoRevisar: () => void;
}) {
  return <section aria-label="Resultado da avaliação" tabIndex={-1} className="mx-auto flex w-full max-w-lg min-w-0 scroll-mt-28 flex-col gap-5 rounded-3xl border border-(--border) bg-(--panel) p-5 text-center [overflow-wrap:anywhere] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-(--focus) sm:p-10">
    <IconeResultado estado="sucesso" />
    <span className="kicker">Avaliação recebida</span>
    <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">Obrigado por contribuir.</h2>
    <div role="status" className="space-y-3 text-sm leading-relaxed text-(--ink-soft)">
      <p>Avaliação registrada com sucesso. Sua contribuição ajudará estudantes a interpretar esta disciplina com mais contexto.</p>
      <p>Se você já tinha uma avaliação para este professor nesta disciplina, ela foi substituída por este envio.</p>
      {avisoComentario && <p className="rounded-xl bg-background p-3 text-foreground">{avisoComentario}</p>}
    </div>
    <div className="rounded-xl border border-(--border) bg-background p-4">
      <p className="font-mono text-xs text-accent">{contexto.codigo}</p>
      <p className="mt-1 font-semibold">{contexto.disciplina}</p>
      <p className="mt-1 text-sm text-(--muted)">{contexto.professor}</p>
    </div>
    <Link href={contexto.resultadosHref} className="button primary">Voltar aos resultados <Icone nome="arrow-right" pequeno /></Link>
    <Link href="/" className="link inline-flex min-h-11 items-center justify-center text-sm">Ir para o início</Link>
    <button type="button" onClick={aoRevisar} className="link min-h-11 text-sm">Revisar ou substituir avaliação</button>
  </section>;
}
