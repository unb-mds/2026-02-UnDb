import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-8 px-4 py-16">
      <div>
        <h1 className="text-3xl font-semibold">Avaliação de Professores UnB</h1>
        <p className="mt-2 text-base text-foreground/70">
          Consulte avaliações estruturadas antes de escolher professor e disciplina — sem precisar de rede de
          contatos.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/professores"
          className="rounded-xl border border-foreground/10 p-5 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
        >
          <span className="text-lg font-medium">Buscar professor</span>
          <span className="mt-1 block text-sm text-foreground/60">Pelo nome, completo ou parcial.</span>
        </Link>

        <Link
          href="/disciplinas"
          className="rounded-xl border border-foreground/10 p-5 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
        >
          <span className="text-lg font-medium">Buscar disciplina</span>
          <span className="mt-1 block text-sm text-foreground/60">Pelo nome ou pelo código.</span>
        </Link>
      </div>
    </main>
  );
}
