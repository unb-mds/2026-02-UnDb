import Link from "next/link";
import type { Metadata } from "next";
import FilaModeracao from "./fila-moderacao";

export const metadata: Metadata = {
  title: "Fila de moderação — UnDb",
  robots: { index: false, follow: false },
};

export default function ModeracaoPage() {
  return (
    <main className="container flex flex-1 flex-col gap-7 py-10 sm:py-14">
      <div>
        <h1 className="page-title">Fila de moderação</h1>
        <p className="lead mt-3 max-w-4xl">Analise comentários pendentes, denunciados e suspensos. As decisões sobre o texto preservam os critérios da avaliação.</p>
      </div>
      <nav aria-label="Filas de moderação" className="flex flex-wrap items-center gap-2 text-sm font-medium"><span aria-current="page" className="inline-flex min-h-11 items-center rounded-full bg-foreground px-4 text-background">Comentários</span><Link href="/moderacao/identidades" className="button pill">Identidades de professores</Link></nav>
      <FilaModeracao />
    </main>
  );
}
