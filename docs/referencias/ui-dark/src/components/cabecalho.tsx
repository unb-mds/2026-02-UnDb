"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import { consultarSessao, EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import BuscaCabecalho from "./busca-cabecalho";

function LinkConta({ destino = "/login", autenticado = false }: { destino?: string; autenticado?: boolean }) {
  return <div className="header-actions"><Link href={destino} aria-label={autenticado ? "Minha conta" : "Conta: entrar ou criar conta"} className="button">{autenticado ? "Minha conta" : "Entrar"}</Link>{!autenticado && <Link href={destino.replace("/login", "/cadastro")} className="button primary">Criar conta</Link>}</div>;
}

function ContaComRetorno() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const [autenticado, setAutenticado] = useState(false);
  useEffect(() => {
    let ativo = true;
    const atualizar = () => { void consultarSessao().then(s => { if (ativo) setAutenticado(s.autenticado); }).catch(() => { if (ativo) setAutenticado(false); }); };
    atualizar();
    window.addEventListener(EVENTO_SESSAO_ALTERADA, atualizar);
    window.addEventListener("focus", atualizar);
    return () => { ativo = false; window.removeEventListener(EVENTO_SESSAO_ALTERADA, atualizar); window.removeEventListener("focus", atualizar); };
  }, []);
  const retorno = ((caminho === "/login" || caminho === "/cadastro") ? retornoAvaliacaoSeguro(parametros.get("returnTo")) : null)
    ?? retornoAvaliacaoSeguro(`${caminho}${parametros.size ? `?${parametros}` : ""}`);
  return <LinkConta autenticado={autenticado} destino={retorno ? `/login?returnTo=${encodeURIComponent(retorno)}` : "/login"} />;
}

export default function Cabecalho() {
  const caminho = usePathname();
  const home = caminho === "/";
  const conta = ["/login", "/cadastro", "/confirmar-email"].includes(caminho);
  return (
    <header className="header">
      <div className="container header-inner">
        <Link href="/" aria-label="UnDb — início" className="brand">
          <span className="brand-mark">U</span><span>Un<span className="code">Db</span></span>
        </Link>
        {home ? <nav aria-label="Navegação principal" className="main-nav"><Link href="/professores">Explorar</Link><Link href="/departamentos">Departamentos</Link><Link href="/disciplinas">Comparar professores</Link></nav> : !conta && <Suspense fallback={<div className="search search-header" aria-label="Carregando busca" />}><BuscaCabecalho /></Suspense>}
        <Suspense fallback={<LinkConta />}><ContaComRetorno /></Suspense>
      </div>
    </header>
  );
}
