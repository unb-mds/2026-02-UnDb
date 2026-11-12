import Link from "next/link";
import BuscaEntrada from "@/components/busca-entrada";
import CatalogoHome from "@/components/catalogo-home";
import Icone, { type NomeIcone } from "@/components/icone";
import MapaVento from "@/components/mapa-vento";
import ResultadoBento from "@/components/resultado-bento";

const PRINCIPIOS = [
  ["Critérios separados", "Didática não vira uma nota geral."],
  ["Base sempre visível", "Você sabe quantas pessoas responderam."],
  ["Privacidade primeiro", "Resultados aparecem a partir de 3 avaliações."],
] as const;

const PASSOS: [NomeIcone, string, string][] = [
  ["search", "Encontre", "Busque por professor, nome da disciplina ou código em uma única entrada."],
  ["compare", "Compare", "Leia didática, dificuldade, chamada, material e recomendação lado a lado."],
  ["check", "Contribua", "Responda critérios objetivos em um formulário curto. O comentário é opcional e passa por moderação humana."],
];

export default function Home() {
  return (
    <main className="flex flex-1 flex-col overflow-x-clip">
      <section className="container pb-16" aria-labelledby="titulo-home">
        <div className="hero-intro">
          <MapaVento className="hero-wind" />
          <p className="eyebrow">Feito por alunos da UnB, para alunos da UnB</p>
          <h1 id="titulo-home" className="hero-title">Escolha seus professores com a opinião de quem já cursou.</h1>
          <p className="hero-copy">Encontre professores e disciplinas. Consulte didática, dificuldade, chamada, material e recomendação, sem cadastro e em qualquer unidade acadêmica.</p>
        </div>
        <div id="busca" className="scroll-mt-28"><BuscaEntrada /></div>

        <aside aria-labelledby="exemplo-titulo" className="glass mx-auto mt-16 flex max-w-[1016px] flex-col gap-6 p-5 sm:p-8">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-(--border) pb-5">
            <div className="grid gap-1">
              <span className="label-mono">Exemplo ilustrativo · dados fictícios</span>
              <span className="font-mono text-sm tracking-wider text-(--ink-soft)">Como um resultado aparece</span>
            </div>
            <span className="pill-count bg-(--accent-soft)! text-accent!">18 respostas</span>
          </div>
          <div>
            <span className="label-mono">Professor nesta disciplina</span>
            <h2 id="exemplo-titulo" className="mt-1 text-2xl font-semibold">Exemplo de professor</h2>
            <p className="text-sm text-(--ink-soft)">Exemplo de disciplina</p>
          </div>
          <ResultadoBento rotulo="Exemplo de resultados agregados" recomenda={92} didatica={4.7} total={18}
            criterios={[
              { rotulo: "Dificuldade", valor: "Médio", legenda: "Resposta mais frequente" },
              { rotulo: "Chamada", valor: "Faz chamada", legenda: "Maioria das respostas" },
              { rotulo: "Material", valor: "Bom", legenda: "Resposta mais frequente" },
            ]} />
          <Link href="/disciplinas" className="button primary self-stretch sm:self-end">Encontrar uma disciplina<Icone nome="arrow-right" pequeno /></Link>
        </aside>
      </section>

      <section aria-label="Princípios do UnDb" className="border-y border-(--border)">
        <div className="container grid sm:grid-cols-3">
          {PRINCIPIOS.map(([titulo, texto]) => <p key={titulo} className="flex flex-col gap-1 border-(--border) py-5 text-center text-sm not-last:border-b sm:px-4 sm:not-last:border-r sm:not-last:border-b-0">
            <strong className="font-medium">{titulo}</strong>
            <span className="text-(--ink-soft)">{texto}</span>
          </p>)}
        </div>
      </section>

      <section aria-labelledby="como-funciona" className="border-b border-(--border) py-16 sm:py-24">
        <div className="container">
          <div className="max-w-xl">
            <span className="kicker">Como funciona</span>
            <h2 id="como-funciona" className="section-title mt-3">Da busca à decisão, critério por critério.</h2>
            <p className="lead mt-4">Vá da busca à comparação e contribua com a mesma estrutura que ajudou você a decidir.</p>
          </div>
          <ol className="mt-12 grid border-t border-(--border) sm:grid-cols-3">
            {PASSOS.map(([icone, titulo, texto], indice) => <li key={titulo} className="relative flex flex-col gap-3 border-(--border) py-8 not-last:border-b sm:px-6 sm:first:pl-0 sm:not-last:border-r sm:not-last:border-b-0">
              <span className="absolute top-5 right-0 font-mono text-xs text-(--muted) sm:right-6" aria-hidden="true">0{indice + 1}</span>
              <span className="grid size-9 place-items-center rounded-full border border-(--border-strong) text-accent"><Icone nome={icone} pequeno /></span>
              <h3 className="mt-6 text-xl font-medium">{titulo}</h3>
              <p className="text-sm leading-relaxed text-(--ink-soft)">{texto}</p>
            </li>)}
          </ol>
        </div>
      </section>

      <section aria-labelledby="sobre-dados" className="container grid gap-10 py-16 sm:py-24 lg:grid-cols-2">
        <div>
          <span className="kicker">Feito para a UnB</span>
          <h2 id="sobre-dados" className="section-title mt-3 max-w-sm">Dados com contexto e cuidado.</h2>
        </div>
        <ul className="border-t border-(--border)">
          {([["shield", "Privacidade por padrão", "Resultados só aparecem a partir de três avaliações. O UnDb não guarda matrícula, CPF ou histórico acadêmico."],
            ["info", "Sem nota geral", "Dificuldade e chamada são informações neutras, não julgamentos. Não há ranking de professores."]] as const).map(([icone, titulo, texto]) =>
            <li key={titulo} className="flex gap-3 border-b border-(--border) py-5 text-sm">
              <span className="mt-0.5 text-(--ink-soft)"><Icone nome={icone} pequeno /></span>
              <span><strong className="block text-base font-medium">{titulo}</strong><span className="text-(--ink-soft)">{texto}</span></span>
            </li>)}
        </ul>
      </section>

      <div className="container flex flex-col gap-16 pb-16">
        <CatalogoHome />
      </div>

      <section aria-labelledby="convite-avaliar" className="container pb-16 sm:pb-24">
        <div className="glass flex flex-col items-start justify-between gap-6 rounded-2xl! p-6 sm:flex-row sm:items-center sm:px-8">
          <div className="max-w-2xl">
            <h2 id="convite-avaliar" className="text-xl font-medium sm:text-2xl">Já cursou? Ajude quem vem depois.</h2>
            <p className="mt-2 text-sm text-(--ink-soft)">Avalie em cinco critérios com sua conta institucional confirmada. Comentários são opcionais e passam por moderação humana.</p>
          </div>
          <Link href="/professores" className="button primary shrink-0">Avaliar um professor<Icone nome="arrow-right" pequeno /></Link>
        </div>
      </section>
    </main>
  );
}
