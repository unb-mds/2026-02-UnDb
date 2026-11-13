import Link from "next/link";
import BuscaEntrada from "@/components/busca-entrada";
import MapaVento from "@/components/mapa-vento";
import Icone from "@/components/icone";
import DestaquesHome from "@/components/destaques-home";
import CatalogoHome from "@/components/catalogo-home";

export default function Home() {
  return <main className="relative isolate flex flex-1 flex-col overflow-x-clip">
    <section aria-labelledby="titulo-home" className="container pb-12">
      <div className="hero-intro">
        <MapaVento className="hero-wind" />
        <p className="eyebrow">Feito por alunos da UnB, para alunos da UnB</p>
        <h1 id="titulo-home" className="hero-title">Escolha seus professores com a opinião de <span className="bg-linear-to-r from-accent to-(--success) bg-clip-text text-transparent">quem já cursou.</span></h1>
        <p className="hero-copy">Encontre professores e disciplinas. Consulte didática, dificuldade, chamada, material e recomendação, sem cadastro e em qualquer unidade acadêmica.</p>
      </div>
      <div id="busca" className="mt-10 scroll-mt-44"><BuscaEntrada /></div>
    </section>
    <section aria-label="Como ler as avaliações" className="border-y border-(--border) bg-(--panel)/40">
      <div className="container grid gap-5 py-6 sm:grid-cols-3 sm:gap-8">
        <div className="flex items-start gap-3 text-sm"><span className="mt-0.5 grid size-10 shrink-0 place-items-center rounded-xl bg-linear-to-br from-(--accent-soft) to-(--success-soft) text-accent"><Icone nome="compare" /></span><p><strong className="block font-medium text-foreground">Cinco critérios, sem nota geral</strong><span className="mt-1 block text-xs leading-relaxed text-(--muted)">Didática, dificuldade, chamada, material e recomendação.</span></p></div>
        <div className="flex items-start gap-3 text-sm"><span className="mt-0.5 grid size-10 shrink-0 place-items-center rounded-xl bg-linear-to-br from-(--accent-soft) to-(--success-soft) text-accent"><Icone nome="book" /></span><p><strong className="block font-medium text-foreground">Experiências com contexto</strong><span className="mt-1 block text-xs leading-relaxed text-(--muted)">Cada professor é avaliado na disciplina que leciona.</span></p></div>
        <div className="flex items-start gap-3 text-sm"><span className="mt-0.5 grid size-10 shrink-0 place-items-center rounded-xl bg-linear-to-br from-(--accent-soft) to-(--success-soft) text-accent"><Icone nome="shield" /></span><p><strong className="block font-medium text-foreground">Privacidade em primeiro lugar</strong><span className="mt-1 block text-xs leading-relaxed text-(--muted)">Critérios disponíveis a partir de três avaliações.</span></p></div>
      </div>
    </section>
    <div className="container flex flex-col gap-10 py-10 sm:py-14">
      <DestaquesHome />
      <CatalogoHome />
      <div className="flex flex-col items-start justify-between gap-4 rounded-2xl border border-(--border) bg-background p-6 sm:flex-row sm:items-center sm:p-6">
        <div><h2 className="text-xl font-medium sm:text-2xl">Já cursou? Ajude quem vem depois.</h2><p className="mt-1 text-sm text-(--muted)">Avalie em cinco critérios com sua conta institucional confirmada. Comentários são opcionais e passam por moderação humana.</p></div>
        <Link href="/professores" className="button primary shrink-0">Avaliar um professor <Icone nome="arrow-right" pequeno /></Link>
      </div>
    </div>
  </main>;
}
