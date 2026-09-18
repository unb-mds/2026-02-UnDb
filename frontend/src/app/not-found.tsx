import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col items-start justify-center gap-3 px-4 py-16">
      <h1 className="text-2xl font-semibold">Não encontramos isso</h1>
      <p className="text-sm text-foreground/70">
        O professor ou a disciplina que você procura não está cadastrado, ou o link está incorreto.
      </p>
      <div className="mt-2 flex gap-4 text-sm font-medium">
        <Link href="/professores" className="text-foreground underline underline-offset-4">
          Buscar professor
        </Link>
        <Link href="/disciplinas" className="text-foreground underline underline-offset-4">
          Buscar disciplina
        </Link>
      </div>
    </main>
  );
}
