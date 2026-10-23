"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Cabecalho() {
  const caminho = usePathname();
  if (caminho === "/prototipo" || caminho.startsWith("/prototipo/")) return null;
  return (
    <header className="border-b border-foreground/10">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
        <Link href="/" aria-label="UnDb — início" className="py-2 text-xl font-semibold text-accent">
          UnDb
        </Link>
        <nav aria-label="Navegação principal" className="flex flex-wrap gap-x-4 gap-y-2 text-sm font-medium">
          <Link href="/professores" className="py-2 hover:text-accent hover:underline underline-offset-4">
            Professores
          </Link>
          <Link href="/disciplinas" className="py-2 hover:text-accent hover:underline underline-offset-4">
            Disciplinas
          </Link>
          <Link href="/login" className="py-2 hover:text-accent hover:underline underline-offset-4">
            Entrar
          </Link>
          <Link href="/cadastro" className="py-2 hover:text-accent hover:underline underline-offset-4">
            Criar conta
          </Link>
        </nav>
      </div>
    </header>
  );
}
