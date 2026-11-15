import Link from "next/link";
import Icone from "@/components/icone";

export default function NotFound() {
  return (
    <main className="container flex flex-1 flex-col items-start justify-center gap-5 py-16 sm:py-28">
      <span className="code-chip">404</span>
      <h1 className="page-title">Não encontramos isso</h1>
      <p className="max-w-xl text-base leading-relaxed text-(--ink-soft)">
        O professor ou a disciplina que você procura não está cadastrado, ou o link está incorreto.
      </p>
      <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
        <Link href="/professores" className="button primary">
          Buscar professor <Icone nome="arrow-right" pequeno />
        </Link>
        <Link href="/disciplinas" className="button text-accent!">
          Buscar disciplina
        </Link>
      </div>
      <Link href="/" className="back-link"><Icone nome="arrow-left" pequeno />Voltar ao início</Link>
    </main>
  );
}
