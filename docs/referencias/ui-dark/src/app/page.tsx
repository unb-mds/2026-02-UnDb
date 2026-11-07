import Link from "next/link";
import { Suspense } from "react";
import BuscaHero from "@/components/busca-hero";
import CatalogoHome from "@/components/catalogo-home";
export const dynamic = "force-dynamic";
export default function Home() {
  return <main className="home-dark"><section className="hero"><div className="container hero-inner">
    <span className="badge outlined hero-tag">Feito por alunos da UnB, para alunos da UnB</span>
    <h1>Escolha seus professores com a<br className="desktop-break" /> opinião de quem já cursou.</h1>
    <p>Consulte didática, dificuldade, chamada, material e recomendação — sem cadastro<br className="desktop-break" /> e em qualquer departamento.</p>
    <BuscaHero /><p className="hero-help">Escolha se procura um professor ou uma disciplina. Digite ao menos 2 caracteres.</p>
    <div className="popular"><span>Explore:</span><Link className="chip" href="/disciplinas?q=FGA0312">Métodos de Desenvolvimento de Software</Link><Link className="chip" href="/disciplinas?q=FGA0313">Requisitos de Software</Link><Link className="chip" href="/disciplinas?q=CIC0002">Fundamentos Teóricos da Computação</Link></div>
  </div></section><div className="container home-content">
    <Suspense fallback={<p role="status">Carregando catálogo…</p>}><CatalogoHome /></Suspense>
    <section className="callout section"><div><h2>Já cursou? Ajude quem vem depois.</h2><p>Avalie em cinco critérios e, se quiser, deixe um comentário. Textos passam por moderação humana.</p></div><Link className="button primary" href="/professores">Avaliar um professor</Link></section>

  </div></main>;
}
