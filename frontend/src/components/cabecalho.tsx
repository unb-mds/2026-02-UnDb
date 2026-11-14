"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import { consultarSessao, EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import Icone from "./icone";

type EstadoSessao = "carregando" | "autenticado" | "visitante" | "erro";

function LinksConta({ retorno, sessao = "carregando" }: { retorno?: string | null; sessao?: EstadoSessao }) {
  const query = retorno ? `?returnTo=${encodeURIComponent(retorno)}` : "";
  return <nav aria-label="Conta" className="header-actions">
    {sessao === "autenticado" ? (
      <Link href="/login" className="button ghost"><Icone nome="user" pequeno />Minha conta</Link>
    ) : <>
      <Link href={`/login${query}`} className="button ghost">{sessao === "visitante" ? "Entrar" : "Verificar conta"}</Link>
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
      setSessao("carregando");
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

const LINKS = [["/professores", "Professores"], ["/disciplinas", "Disciplinas"], ["/departamentos", "Unidades acadêmicas"], ["/sobre", "Sobre"]] as const;

function NavegacaoPrincipal({ caminho }: { caminho: string }) {
  return <nav aria-label="Navegação principal" className="main-nav">
    <Link href={caminho === "/" ? "#busca" : "/#busca"} className="nav-search"><Icone nome="search" pequeno />Buscar</Link>
    {LINKS.map(([href, nome]) => <Link key={href} href={href} aria-current={caminho === href ? "page" : undefined}>{nome}</Link>)}
  </nav>;
}

export default function Cabecalho() {
  const caminho = usePathname();
  // O menu do celular guarda a página em que foi aberto: ao navegar, deixa de valer e fecha sozinho.
  const [abertoEm, setAbertoEm] = useState<string | null>(null);
  const aberto = abertoEm === caminho;
  if (caminho === "/prototipo" || caminho.startsWith("/prototipo/")) return null;
  return <header className="header" data-aberto={aberto ? "true" : undefined}><div className="container header-inner">
    <Link href="/" aria-label="UnDb — início" className="brand"><Image src="/brand/undb-logo.png" alt="" width={600} height={201} className="brand-logo" loading="eager" /></Link>
    <button type="button" className="menu-toggle" aria-expanded={aberto} aria-controls="menu-principal" aria-label={aberto ? "Fechar menu" : "Abrir menu"} onClick={() => setAbertoEm(aberto ? null : caminho)}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">{aberto ? <><path d="m6 6 12 12" /><path d="m18 6-12 12" /></> : <><path d="M4 7h16" /><path d="M4 12h16" /><path d="M4 17h16" /></>}</svg>
    </button>
    <div className="header-center" id="menu-principal">
      <NavegacaoPrincipal caminho={caminho} />
    </div>
    <Suspense fallback={<LinksConta />}><ContaComRetorno /></Suspense>
  </div></header>;
}
