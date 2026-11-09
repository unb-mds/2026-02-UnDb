import Link from "next/link";
import BuscaEntrada from "@/components/busca-entrada";
import CatalogoHome from "@/components/catalogo-home";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col">
      <section className="border-b border-(--border) bg-linear-to-b from-(--primary)/25 to-background py-12 sm:py-20">
        <div className="container flex flex-col items-center gap-6 text-center">
          <span className="rounded-full border border-accent/40 px-4 py-2 text-xs text-accent">Feito por alunos da UnB, para alunos da UnB</span>
          <h1 className="max-w-4xl text-3xl leading-tight font-bold tracking-tight sm:text-5xl">Escolha seus professores com a opinião de quem já cursou.</h1>
          <p className="max-w-2xl text-base text-(--muted)">Encontre professores e disciplinas. Consulte didática, dificuldade, chamada, material e recomendação — sem cadastro e em qualquer unidade acadêmica.</p>
          <div className="w-full max-w-3xl"><BuscaEntrada /></div>
        </div>
      </section>
      <div className="container flex flex-col gap-12 py-10 sm:py-14">
        <CatalogoHome />
        <section className="flex flex-col items-start justify-between gap-6 rounded-2xl border border-accent/30 bg-(--primary)/10 p-6 sm:flex-row sm:items-center sm:p-8">
          <div className="max-w-2xl">
            <h2 className="text-2xl font-semibold">Já cursou? Ajude quem vem depois.</h2>
            <p className="mt-2 text-sm text-(--muted)">Avalie em cinco critérios com sua conta institucional confirmada. Comentários são opcionais e passam por moderação humana.</p>
          </div>
          <Link href="/professores" className="button primary shrink-0">Avaliar um professor</Link>
        </section>
      </div>
    </main>
  );
}
