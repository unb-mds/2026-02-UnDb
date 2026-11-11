import type { Metadata } from "next";
import Link from "next/link";
import FilaIdentidades from "./fila-identidades";
export const metadata: Metadata = { title: "Identidades de professores — UnDb", robots: { index: false, follow: false } };
export default function Page() {
  return <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
    <nav aria-label="Filas de moderação" className="flex flex-wrap gap-4"><Link href="/moderacao">Comentários</Link><span aria-current="page">Identidades de professores</span></nav>
    <header><h1 className="text-2xl font-semibold">Identidades de professores</h1><p className="mt-2 text-foreground/70">Confira as dúvidas da importação com as evidências institucionais. Confirmar uma associação agenda sua aplicação; avaliações conflitantes nunca são descartadas.</p></header>
    <FilaIdentidades />
  </main>;
}
