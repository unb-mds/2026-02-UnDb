"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import { consultarSessao, EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import BuscaCabecalho from "./busca-cabecalho";

type EstadoSessao = "carregando" | "autenticado" | "visitante" | "erro";

function LinksConta({ retorno, sessao = "carregando" }: { retorno?: string | null; sessao?: EstadoSessao }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <nav aria-label="Conta" className="header-actions">
    {sessao === "autenticado" ? (
      <Link href="/login" className="button primary">Minha conta</Link>
    ) : <>
      <Link href={`/login${query}`} className="button">Entrar ou criar conta</Link>
      {sessao !== "visitante" && <span className="sr-only" role="status">{sessao === "carregando" ? "Verificando sessão…" : "Não foi possível verificar a sessão. Acesse a conta para tentar novamente."}</span>}
    </>}
  </nav>;
}

function ContaComRetorno() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const [sessao, setSessao] = useState<EstadoSessao>("carregando");

  useEffect(() => {
    let geracao = 0;
    let ativo = true;
    const atualizar = async () => {
      const atual = ++geracao;
      try {
        const resposta = await consultarSessao();
        if (ativo && atual === geracao) setSessao(resposta.autenticado ? "autenticado" : "visitante");
      } catch {
        if (ativo && atual === geracao) setSessao("erro");
      }
    };
    const aoFicarVisivel = () => {
      if (document.visibilityState === "visible") void atualizar();
      else ++geracao;
    };
    void atualizar();
    window.addEventListener(EVENTO_SESSAO_ALTERADA, atualizar);
    window.addEventListener("focus", atualizar);
    window.addEventListener("pageshow", atualizar);
    document.addEventListener("visibilitychange", aoFicarVisivel);
    return () => {
      ativo = false;
      ++geracao;
      window.removeEventListener(EVENTO_SESSAO_ALTERADA, atualizar);
      window.removeEventListener("focus", atualizar);
      window.removeEventListener("pageshow", atualizar);
      document.removeEventListener("visibilitychange", aoFicarVisivel);
    };
  }, [caminho]);

  const retorno = (["/login", "/cadastro"].includes(caminho) ? retornoAvaliacaoSeguro(parametros.get("returnTo")) : null)
    ?? retornoAvaliacaoSeguro(`${caminho}${parametros.size ? `?${parametros}` : ""}`);
  return <LinksConta retorno={retorno} sessao={sessao} />;
}

export default function Cabecalho() {
  const caminho = usePathname();
  if (caminho === "/prototipo" || caminho.startsWith("/prototipo/")) return null;
  const home = caminho === "/";
  const conta = ["/login", "/cadastro", "/confirmar-email"].includes(caminho);
  return <header className="header"><div className="container header-inner">
    <Link href="/" aria-label="UnDb — início" className="brand"><Image src="/brand/undb-logo.png" alt="" width={600} height={201} className="brand-logo" loading="eager" /></Link>
    {home ? <nav aria-label="Navegação principal" className="main-nav"><Link href="/professores">Professores</Link><Link href="/disciplinas">Disciplinas</Link><Link href="/departamentos">Unidades acadêmicas</Link><Link href="/disciplinas">Comparar professores</Link></nav>
      : !conta && <Suspense fallback={<div className="search search-header" role="status">Carregando busca…</div>}><BuscaCabecalho /></Suspense>}
    <Suspense fallback={<LinksConta />}><ContaComRetorno /></Suspense>
  </div></header>;
}
