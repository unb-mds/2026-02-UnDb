import Link from "next/link";
import BuscaEntrada from "@/components/busca-entrada";
import EtapasJornada from "@/components/etapas-jornada";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <EtapasJornada atual={0} />
      <div>
        <h1 className="text-2xl font-semibold">Encontre professores e disciplinas</h1>
        <p className="mt-2 text-base text-foreground/70">
          Consulte e compare sem cadastro. Para enviar uma avaliação, entre com sua conta de e-mail institucional confirmado.
        </p>
      </div>

      <div className="flex w-full max-w-2xl flex-col gap-6">
        <BuscaEntrada />
        <div className="grid gap-4 sm:grid-cols-2">
          <Link
            href="/professores"
            className="rounded-xl border border-foreground/10 p-5 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
          >
            <span className="text-lg font-medium">Buscar professor</span>
            <span className="mt-1 block text-sm text-foreground/70">Veja as disciplinas agrupadas e escolha qual deseja consultar ou avaliar.</span>
          </Link>

          <Link
            href="/disciplinas"
            className="rounded-xl border border-foreground/10 p-5 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
          >
            <span className="text-lg font-medium">Buscar disciplina</span>
            <span className="mt-1 block text-sm text-foreground/70">Encontre a matéria pelo nome ou código e compare seus professores.</span>
          </Link>
        </div>
      </div>
      <details className="text-sm text-foreground/70">
        <summary className="cursor-pointer py-2 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">Sobre a demonstração da jornada</summary>
        <Link href="/prototipo" className="mt-2 inline-block text-accent underline underline-offset-4">
          Experimentar o protótipo da jornada · dados demonstrativos →
        </Link>
      </details>
    </main>
  );
}
