"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";

function LinkConta({ destino = "/login" }: { destino?: string }) {
  return <Link href={destino} aria-label="Conta: entrar ou criar conta" className="rounded-lg border border-foreground/20 px-3 py-2 text-accent hover:underline underline-offset-4">Entrar / Criar conta</Link>;
}

function ContaComRetorno() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const retorno = ((caminho === "/login" || caminho === "/cadastro") ? retornoAvaliacaoSeguro(parametros.get("returnTo")) : null)
    ?? retornoAvaliacaoSeguro(`${caminho}${parametros.size ? `?${parametros}` : ""}`);
  return <LinkConta destino={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"} />;
}

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
          <Suspense fallback={<LinkConta />}><ContaComRetorno /></Suspense>
        </nav>
      </div>
    </header>
  );
}
