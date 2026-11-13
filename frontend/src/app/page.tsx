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
      <div id="busca" className="scroll-mt-44"><BuscaEntrada /></div>
      <div className="mx-auto mt-8 grid max-w-[720px] gap-3 sm:grid-cols-2">
        <Link href="/professores" className="group flex min-w-0 items-center gap-4 rounded-2xl border border-(--border) bg-(--panel)/70 p-5 transition-colors hover:border-accent/60 hover:bg-(--surface-accent)/50">
          <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-(--accent-soft)/60 text-accent"><Icone nome="user" /></span>
          <span className="min-w-0 flex-1"><span className="block font-medium">Explorar professores</span><span className="mt-1 block text-xs leading-relaxed text-(--muted)">Encontre pelo nome e veja as disciplinas.</span></span><span className="text-(--muted) group-hover:text-accent"><Icone nome="arrow-right" pequeno /></span>
        </Link>
        <Link href="/disciplinas" className="group flex min-w-0 items-center gap-4 rounded-2xl border border-(--border) bg-(--panel)/70 p-5 transition-colors hover:border-(--success)/60 hover:bg-(--success-soft)/40">
          <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-(--success-soft)/70 text-(--success)"><Icone nome="book" /></span>
          <span className="min-w-0 flex-1"><span className="block font-medium">Explorar disciplinas</span><span className="mt-1 block text-xs leading-relaxed text-(--muted)">Encontre a matéria e compare professores.</span></span><span className="text-(--muted) group-hover:text-(--success)"><Icone nome="arrow-right" pequeno /></span>
        </Link>
      </div>
      <p className="mt-6 flex items-center justify-center gap-2 text-center text-xs leading-relaxed text-(--muted)"><Icone nome="shield" pequeno />Consulta pública. Entre na conta só para avaliar.</p>
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
      <details className="group border-t border-(--border) pt-5 text-sm">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-4 font-medium">Primeira vez por aqui? Veja como funciona.<span aria-hidden="true" className="text-accent group-open:rotate-90"><Icone nome="arrow-right" pequeno /></span></summary>
        <ol className="mt-4 grid gap-5 pb-4 text-sm text-(--ink-soft) sm:grid-cols-3">
          <li><strong className="mb-1 block text-foreground">01 · Encontre</strong>Busque pelo nome do professor, da disciplina ou pelo código.</li>
          <li><strong className="mb-1 block text-foreground">02 · Compare</strong>Leia cada critério e a quantidade de avaliações. Dificuldade e chamada são informações neutras.</li>
          <li><strong className="mb-1 block text-foreground">03 · Contribua</strong>Avalie com sua conta institucional confirmada. Comentários são opcionais e passam por moderação humana.</li>
        </ol>
      </details>
      <div className="flex flex-col items-start justify-between gap-4 rounded-2xl border border-(--border) bg-background p-6 sm:flex-row sm:items-center sm:p-6">
        <div><h2 className="text-xl font-medium sm:text-2xl">Já cursou? Ajude quem vem depois.</h2><p className="mt-1 text-sm text-(--muted)">Avalie em cinco critérios com sua conta institucional confirmada. Comentários são opcionais e passam por moderação humana.</p></div>
        <Link href="/professores" className="button primary shrink-0">Avaliar um professor <Icone nome="arrow-right" pequeno /></Link>
      </div>
    </div>
  </main>;
}
