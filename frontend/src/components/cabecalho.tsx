"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import BuscaCabecalho from "./busca-cabecalho";

function LinksConta({ retorno }: { retorno?: string | null }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <div className="header-actions">
    <Link href={`/login${query}`} aria-label="Conta: entrar ou criar conta" className="button">Entrar</Link>
    <Link href={`/cadastro${query}`} className="button primary">Criar conta</Link>
  </div>;
}

function ContaComRetorno() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const retorno = (["/login", "/cadastro"].includes(caminho) ? retornoAvaliacaoSeguro(parametros.get("returnTo")) : null)
    ?? retornoAvaliacaoSeguro(`${caminho}${parametros.size ? `?${parametros}` : ""}`);
  return <LinksConta retorno={retorno} />;
}

export default function Cabecalho() {
  const caminho = usePathname();
  if (caminho === "/prototipo" || caminho.startsWith("/prototipo/")) return null;
  const home = caminho === "/";
  const conta = ["/login", "/cadastro", "/confirmar-email"].includes(caminho);
  return <header className="header"><div className="container header-inner">
    <Link href="/" aria-label="UnDb — início" className="brand"><span className="brand-mark" aria-hidden="true">U</span><span>Un<span className="brand-accent">Db</span></span></Link>
    {home ? <nav aria-label="Navegação principal" className="main-nav"><Link href="/professores">Professores</Link><Link href="/disciplinas">Disciplinas</Link><Link href="/departamentos">Unidades acadêmicas</Link><Link href="/disciplinas">Comparar professores</Link></nav>
      : !conta && <Suspense fallback={<div className="search search-header" role="status">Carregando busca…</div>}><BuscaCabecalho /></Suspense>}
    <Suspense fallback={<LinksConta />}><ContaComRetorno /></Suspense>
  </div></header>;
}
