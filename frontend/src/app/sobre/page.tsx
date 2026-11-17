import IconeSocial from "@/components/icone-social";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import Icone from "@/components/icone";
import { equipe } from "./equipe";
import { metadadosCompartilhamento } from "@/lib/metadados-compartilhamento";

const titulo = "Sobre o UnDb";
const descricao = "Conheça a proposta do UnDb e a equipe que constrói a plataforma.";
export const metadata: Metadata = {
  alternates: { canonical: "https://undb.app.br/sobre" },
  title: titulo,
  description: descricao,
  openGraph: { ...metadadosCompartilhamento.openGraph, title: titulo, description: descricao, url: "https://undb.app.br/sobre" },
  twitter: { ...metadadosCompartilhamento.twitter, title: titulo, description: descricao },
};

export default function Sobre() {
  return <main className="flex flex-1 flex-col">
    <section className="relative isolate overflow-hidden border-b border-(--border)">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-linear-to-br from-(--brand-blue)/25 via-background to-(--brand-green)/15" />
      <div className="container py-14 sm:py-20">
        <span className="kicker">Sobre o UnDb</span>
        <h1 className="mt-5 max-w-4xl text-4xl leading-tight font-semibold tracking-tight sm:text-6xl">Mais contexto para escolher.<br /><span className="bg-linear-to-r from-accent to-(--success) bg-clip-text text-transparent">Mais vozes para ajudar.</span></h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-(--ink-soft) sm:text-lg">Uma plataforma feita por estudantes para compartilhar experiências sobre professores e disciplinas da UnB. Para que uma boa decisão não dependa só de conhecer a pessoa certa.</p>
        <nav aria-label="Nesta página" className="mt-8 flex flex-wrap gap-3"><Link href="#proposta" className="button">Nossa proposta</Link><Link href="#metodologia" className="button">Metodologia e limites</Link><Link href="#equipe" className="button primary">Conheça a equipe <Icone nome="arrow-right" pequeno /></Link></nav>
      </div>
    </section>
    <div className="container flex flex-col gap-14 py-12 sm:gap-20 sm:py-16">
      <section aria-label="Contato"><p className="mb-4 text-sm"><Link href="/privacidade" className="link">Política de Privacidade</Link> · <Link href="/termos-de-uso" className="link">Termos de Uso</Link></p><h2 className="section-title">Precisa falar com a equipe?</h2><p>Informe erros institucionais, conteste conteúdo ou solicite atendimento sobre dados pessoais.</p><Link href="/contato" className="button">Contato e solicitações</Link></section>
      <section id="proposta" aria-labelledby="proposta-titulo" className="grid scroll-mt-48 gap-8 lg:grid-cols-[1fr_1.5fr] lg:gap-16">
        <div><span className="kicker">Por que existimos</span><h2 id="proposta-titulo" className="section-title mt-3">Experiências que ajudam<br />a próxima turma.</h2></div>
        <div className="space-y-4 text-base leading-relaxed text-(--ink-soft)"><p>Antes de montar o semestre, surgem perguntas que a oferta de disciplinas não responde: como são as explicações? Qual é o ritmo das aulas? Há material de apoio?</p><p>O UnDb reúne avaliações estruturadas para tornar essas experiências mais fáceis de consultar. Cada avaliação pertence a um professor em uma disciplina específica, preservando o contexto professor–disciplina.</p><p>O UnDb é um projeto acadêmico estudantil independente e sem fins lucrativos. Sua motivação é facilitar o acesso a experiências que circulam em contatos pessoais. É uma fonte complementar aos processos oficiais de avaliação e matrícula da UnB, sem representar autorização ou endosso institucional.</p><p>Nosso objetivo é apoiar escolhas informadas e contribuições respeitosas, sem reduzir o trabalho de um professor a uma nota geral.</p></div>
      </section>
      <section aria-labelledby="principios-titulo"><span className="kicker">Como cuidamos da informação</span><h2 id="principios-titulo" className="section-title mt-3">Clareza, contexto e cuidado.</h2><div className="mt-7 grid gap-4 md:grid-cols-3">
        {([
          ["compare", "Cinco critérios separados", "Didática, dificuldade, chamada, material e recomendação. Dificuldade e chamada são informativas, sem indicação de bom ou ruim."],
          ["shield", "Autoria da conta não divulgada", "A consulta pública não mostra a identidade da conta autora. O vínculo com a avaliação é mantido internamente; texto livre pode conter pistas de identificação."],
          ["user", "Comentários com responsabilidade", "Comentários são opcionais e podem ser denunciados. Com a triagem automática habilitada, textos sem sinais locais e da IA podem ser publicados automaticamente; os demais aguardam revisão humana."],
        ] as const).map(([icone, titulo, texto]) => <article key={titulo} className="rounded-2xl border border-(--border) bg-(--panel) p-6"><span className="mb-5 grid size-11 place-items-center rounded-xl bg-linear-to-br from-(--accent-soft) to-(--success-soft) text-accent"><Icone nome={icone} /></span><h3 className="text-lg font-medium">{titulo}</h3><p className="mt-3 text-sm leading-relaxed text-(--muted)">{texto}</p></article>)}
      </div></section>
      <section id="metodologia" aria-labelledby="metodologia-titulo" className="scroll-mt-48">
        <span className="kicker">Como ler os resultados</span>
        <h2 id="metodologia-titulo" className="section-title mt-3">Metodologia e limites.</h2>
        <div className="mt-6 space-y-5 text-base leading-relaxed text-(--ink-soft)">
          <p>Os indicadores são calculados por professor e disciplina. A partir de três avaliações, os critérios agregados ficam disponíveis. Com zero, uma ou duas, mostramos a contagem e a insuficiência de dados, sem valores dos critérios. Esse mínimo se aplica aos indicadores, não à publicação de comentários, e não garante anonimato.</p>
          <dl className="grid gap-5 md:grid-cols-2">
            <div className="md:col-span-2"><dt className="font-medium text-foreground">Exclusão e registros de acesso</dt><dd>As regras implementadas preveem exclusão lógica da conta: nome, senha, sessões e links são removidos; identificador, e-mail e datas permanecem, com login bloqueado e e-mail reservado, sem reativação por recadastro. Avaliações e comentários excluídos ficam ocultos imediatamente, com purga após a janela padrão de sete dias. Registros privados das operações de acesso têm retenção padrão de seis meses corridos, sem senha, token ou texto de avaliação. A operação desses mecanismos na hospedagem e os fundamentos e prazos das guardas ainda estão pendentes de validação.</dd></div>
            <div><dt className="font-medium text-foreground">Didática</dt><dd>Média das notas de 1 a 5, com uma casa decimal. Metades são arredondadas para cima.</dd></div>
            <div><dt className="font-medium text-foreground">Dificuldade</dt><dd>Categoria mais frequente (moda). No empate, a prioridade é Difícil, depois Médio, depois Fácil.</dd></div>
            <div><dt className="font-medium text-foreground">Chamada</dt><dd>Indica controle de presença: maioria das respostas Sim ou Não. Empate exato aparece como conflitante. Chamada e dificuldade são informações neutras, sem direção boa ou ruim.</dd></div>
            <div><dt className="font-medium text-foreground">Material</dt><dd>Disponibilidade por maioria de Sim ou Não; empate exato é conflitante. Só com maioria de Sim mostramos a qualidade: moda entre as respostas que informam material disponível, com prioridade Bom, Médio, Ruim no empate.</dd></div>
            <div><dt className="font-medium text-foreground">Recomendação</dt><dd>Percentual de respostas Sim sobre o total, arredondado ao inteiro, com metades para cima. Não é uma nota geral.</dd></div>
            <div><dt className="font-medium text-foreground">Contagem e comparação</dt><dd>A contagem informa quantas avaliações sustentam o resultado. A comparação ordena por recomendação decrescente; empates usam mais avaliações e depois nome alfabético. Resultados insuficientes ficam no final. Destaques por volume não indicam qualidade.</dd></div>
          </dl>
          <p>As opiniões são subjetivas. Amostras pequenas podem representar poucas experiências e os resultados podem mudar ao longo do tempo, inclusive com novas avaliações ou substituições. Não há garantia de veracidade dos relatos ou de representatividade da turma. Uma conta institucional confirmada comprova a confirmação do endereço de e-mail, não matrícula nem experiência na disciplina.</p>
          <p>A triagem usa filtro local e IA quando habilitada. Sinais, possível exposição de dados, falhas, limites ou configuração incompleta mantêm o texto pendente para revisão humana; não há rejeição automática. Sem habilitação, a aprovação humana é prévia. A ausência de sinais não garante adequação nem detecção de todo conteúdo problemático. A moderação do texto não altera os critérios estruturados.</p>
        </div>
      </section>
      <section id="equipe" aria-labelledby="equipe-titulo" className="scroll-mt-48">
        <div className="max-w-2xl"><span className="kicker">Quem está por trás</span><h2 id="equipe-titulo" className="section-title mt-3">Pessoas que constroem o UnDb.</h2><p className="lead mt-4">Conheça a equipe que transforma essa ideia em uma ferramenta para a comunidade.</p></div>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {equipe.map((p, i) => <article key={p.github} className="group relative overflow-hidden rounded-2xl border border-(--border) bg-linear-to-br from-(--surface-accent)/60 via-(--panel) to-(--success-soft)/40 p-7 transition-colors hover:border-accent/60">
            <span aria-hidden="true" className="absolute top-5 right-6 font-mono text-xs text-(--muted)">0{i + 1}</span>
            <div className="relative mb-6 h-32 w-28 overflow-hidden rounded-2xl border border-accent/25 bg-linear-to-br from-(--accent-soft) via-(--brand-blue) to-(--brand-green) shadow-lg shadow-(--brand-blue)/10">
              {p.foto ? <Image src={p.foto} alt={`Retrato de ${p.nome}`} fill sizes="112px" className="object-cover" /> : <span aria-hidden="true" className="grid size-full place-items-center text-4xl font-medium text-foreground">{p.nome.slice(0, 1)}</span>}
            </div>
            <h3 className="text-2xl font-semibold">{p.nome}</h3><p className="mt-2 text-sm text-(--success)">Equipe UnDb</p>
            {p.apresentacao && <p className="mt-4 text-sm leading-relaxed text-(--ink-soft)">{p.apresentacao}</p>}
            <div className="mt-6 flex flex-wrap gap-3">
              <a href={`https://github.com/${p.github}`} target="_blank" rel="noopener noreferrer" aria-label={`GitHub de ${p.nome}, abre em outra aba`} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-(--border-strong) bg-background/40 px-3 text-sm text-(--ink-soft) transition-colors hover:border-accent hover:text-accent"><IconeSocial rede="github" />GitHub</a>
              {p.linkedin ? <a href={p.linkedin} target="_blank" rel="noopener noreferrer" aria-label={`LinkedIn de ${p.nome}, abre em outra aba`} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-accent/30 bg-(--surface-accent)/50 px-3 text-sm text-accent transition-colors hover:border-accent"><IconeSocial rede="linkedin" />LinkedIn</a> : <span className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-(--border) px-3 text-xs text-(--muted)"><IconeSocial rede="linkedin" />LinkedIn não informado</span>}
            </div>
          </article>)}
        </div>
      </section>
      <section aria-labelledby="dados-sobre" className="grid gap-6 rounded-2xl border border-(--border) bg-(--panel) p-6 sm:p-8 lg:grid-cols-2"><div><span className="kicker">De onde vêm os dados</span><h2 id="dados-sobre" className="mt-3 text-2xl font-medium">Catálogo e experiências têm origens diferentes.</h2></div><div className="space-y-4 text-sm leading-relaxed text-(--ink-soft)"><p>As informações institucionais sobre disciplinas, professores e ofertas têm origem nos dados públicos do SIGAA. As avaliações e os comentários são contribuições de estudantes.</p><p>O conteúdo expressa experiências individuais. Quantidade de respostas, disciplina e critérios devem ser considerados juntos na leitura.</p></div></section>
      <div className="flex flex-wrap items-center justify-between gap-5 border-t border-(--border) pt-8"><p className="text-lg font-medium">Seu próximo semestre começa com mais contexto.</p><Link href="/#busca" className="button primary">Encontrar uma disciplina <Icone nome="arrow-right" pequeno /></Link></div>
    </div>
  </main>;
}
