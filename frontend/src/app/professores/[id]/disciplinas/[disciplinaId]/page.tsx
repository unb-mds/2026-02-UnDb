import { nomeUnidade } from "@/lib/unidade";
import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { listarComentariosPublicados } from "@/lib/services/comentarios";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import { iniciaisProfessor } from "@/lib/iniciais";
import FundoLiquido from "@/components/fundo-liquido";
import Icone from "@/components/icone";
import ResultadoBento from "@/components/resultado-bento";
import Caminho from "@/components/caminho";
import SecaoComentarios from "@/components/secao-comentarios";

const MIN_AVALIACOES_EXIBICAO = 3;

export default async function AvaliacaoAgregadaPage({
  params,
  searchParams,
}: {
  searchParams: Promise<ParametrosBusca>;
  params: Promise<{ id: string; disciplinaId: string }>;
}) {
  const { id, disciplinaId } = await params;
  const contexto = lerContextoBusca(await searchParams);
  if (!identificadorValido(id) || !identificadorValido(disciplinaId)) notFound();

  const avaliacao = await consultarAvaliacaoAgregada(id, disciplinaId).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });

  const [comentarios, comparacao] = await Promise.all([
    listarComentariosPublicados(id, disciplinaId).catch(() => null),
    compararProfessoresDaDisciplina(disciplinaId).catch(() => null),
  ]);

  const outrosProfessores = comparacao
    ? comparacao.professores.filter((p) => p.professorId !== id)
    : [];

  const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", RUIM: "Ruim", BOM: "Bom" } as const;
  const total = avaliacao.totalAvaliacoes;
  const avaliacaoHref = comContextoBusca(`/professores/${id}/disciplinas/${disciplinaId}/avaliar`, contexto);

  return (
    <main className="relative isolate flex flex-1 flex-col overflow-hidden">
      <FundoLiquido />
      <div className="container flex max-w-[1088px]! flex-col gap-8 py-8 sm:py-12">
        <Caminho
          itens={[
            { nome: "Início", href: "/" },
            {
              nome: contexto ? "Resultados da busca" : "Professores",
              href: contexto ? urlBusca(contexto) : "/professores",
              retornoBusca: !!contexto,
            },
            {
              nome: avaliacao.disciplina.codigo,
              href: comContextoBusca(`/disciplinas/${disciplinaId}`, contexto),
            },
            { nome: avaliacao.professor.nome },
          ]}
        />

        <div className="-mt-4 flex flex-wrap gap-x-6">
          {contexto && (
            <Link href={urlBusca(contexto)} className="back-link">
              <Icone nome="arrow-left" pequeno /> Voltar aos resultados da busca
            </Link>
          )}
          <Link href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)} className="back-link">
            <Icone nome="arrow-left" pequeno /> Voltar à comparação
          </Link>
          <Link href={comContextoBusca(`/professores/${id}`, contexto)} className="back-link">
            <Icone nome="arrow-left" pequeno /> Voltar para {avaliacao.professor.nome}
          </Link>
        </div>

        <header className="flex min-w-0 items-center gap-5">
          <span className="avatar-initials large" aria-hidden="true">{iniciaisProfessor(avaliacao.professor.nome)}</span>
          <div className="min-w-0">
            <span className="kicker">Professor</span>
            <h1 className="page-title mt-1 break-words">{avaliacao.professor.nome}</h1>
            <p className="lead mt-2">{nomeUnidade(avaliacao.professor)}</p>
          </div>
        </header>

        <section aria-label="Disciplina consultada" className="glass flex flex-col items-start justify-between gap-5 rounded-2xl! p-5 sm:flex-row sm:items-center sm:px-6">
          <div className="flex min-w-0 flex-col items-start gap-2 break-words">
            <span className="code-chip"><span className="sr-only">Código da disciplina: </span>{avaliacao.disciplina.codigo}</span>
            <h2 className="text-xl font-medium">{avaliacao.disciplina.nome}</h2>
            <p className="text-sm text-(--ink-soft)">Unidade acadêmica: {nomeUnidade(avaliacao.disciplina)}</p>
          </div>
          <div className="flex w-full shrink-0 flex-col gap-2 sm:w-auto">
            <Link className="button primary" href={avaliacaoHref}>
              Avaliar este professor na disciplina <Icone nome="arrow-right" pequeno />
            </Link>
            <Link className="button" href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}>
              Comparar professores desta disciplina
            </Link>
            <p className="text-xs text-(--muted)">Avaliar exige e-mail institucional confirmado.</p>
          </div>
        </section>

        {!avaliacao.dadosSuficientes ? (
          <section aria-labelledby="dados-titulo" className="glass flex flex-col items-start gap-3 p-6 sm:p-10">
            <span className="text-accent"><Icone nome="shield" /></span>
            {total === 0 ? (
              <>
                <h2 id="dados-titulo" className="text-xl font-medium">Sem avaliações registradas</h2>
                <p className="max-w-xl text-sm leading-relaxed text-(--ink-soft)">
                  Ainda não há avaliações para este professor nesta disciplina. A falta de avaliações não significa uma nota baixa — seja o primeiro a avaliar!
                </p>
              </>
            ) : (
              <>
                <h2 id="dados-titulo" className="text-xl font-medium">Dados insuficientes para exibir os critérios</h2>
                <p className="max-w-xl text-sm leading-relaxed text-(--ink-soft)">
                  Baseado em {total} avaliaç{total === 1 ? "ão" : "ões"}. São necessárias pelo menos{" "}
                  {MIN_AVALIACOES_EXIBICAO} avaliações para proteger o anonimato de quem avaliou. Faltam{" "}
                  {MIN_AVALIACOES_EXIBICAO - total}.
                </p>
              </>
            )}
            <Link className="button primary mt-2" href={avaliacaoHref}>Contribuir com uma avaliação</Link>
          </section>
        ) : (
          <section aria-labelledby="criterios-titulo" className="flex flex-col gap-6">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <span className="kicker">Resultados agregados</span>
                <h2 id="criterios-titulo" className="section-title mt-2">Os cinco critérios</h2>
                <p className="mt-2 max-w-2xl text-sm text-(--ink-soft)">
                  Baseado em {total} {total === 1 ? "avaliação" : "avaliações"}. Dificuldade e chamada não indicam algo bom ou ruim — são informativos.
                </p>
              </div>
              <span className="pill-count">{total} {total === 1 ? "avaliação" : "avaliações"}</span>
            </div>
            <ResultadoBento
              rotulo="Resultados agregados"
              recomenda={avaliacao.recomenda}
              didatica={avaliacao.didatica}
              total={total}
              criterios={[
                { rotulo: "Dificuldade", valor: rotulos[avaliacao.dificuldade], legenda: "Resposta mais frequente" },
                { rotulo: "Chamada", valor: avaliacao.chamada === "CONFLITANTE" ? "Conflitante" : avaliacao.chamada ? "Faz chamada" : "Não faz chamada", legenda: "Maioria das respostas" },
                {
                  rotulo: "Material",
                  valor: avaliacao.disponibilizaMaterial === "CONFLITANTE"
                    ? "Conflitante"
                    : !avaliacao.disponibilizaMaterial
                      ? "Não disponibiliza"
                      : avaliacao.qualidadeMaterial ? rotulos[avaliacao.qualidadeMaterial] : "Disponibiliza",
                  legenda: avaliacao.disponibilizaMaterial === true ? "Disponibiliza · qualidade mais frequente" : "Disponibilidade da maioria",
                },
              ]}
            />
          </section>
        )}

        <div className="two-columns profile-explanation">
          <section className="glass related rounded-2xl!">
            <h2>Outros professores desta disciplina</h2>
            {comparacao === null ? (
              <p role="alert" className="text-sm mt-2">
                Não foi possível carregar os outros professores. Recarregue a página para tentar novamente.
              </p>
            ) : outrosProfessores.length > 0 ? (
              outrosProfessores.map((p) => (
                <Link
                  key={p.professorId}
                  className="related-row"
                  href={comContextoBusca(`/professores/${p.professorId}/disciplinas/${disciplinaId}`, contexto)}
                >
                  <span>
                    {p.professor.nome}
                    <small>
                      {p.totalAvaliacoes} {p.totalAvaliacoes === 1 ? "avaliação" : "avaliações"}
                    </small>
                  </span>
                  <span className={p.dadosSuficientes ? "code" : "muted"}>
                    {p.dadosSuficientes ? `${p.recomenda}% recomendam` : "Dados insuficientes"}
                  </span>
                </Link>
              ))
            ) : (
              <p className="text-sm text-(--muted) mt-2">Nenhum outro professor cadastrado nesta disciplina.</p>
            )}
            <div className="mt-4">
              <Link className="link text-sm" href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}>
                Abrir comparação completa →
              </Link>
            </div>
          </section>

          <aside className="info-panel note block!">
            <h2 className="flex items-center gap-2"><Icone nome="info" /> Como ler estes números</h2>
            <ul>
              <li>Didática é a média de 1 a 5. Dificuldade e qualidade do material mostram a resposta mais frequente.</li>
              <li>Chamada e disponibilidade de material seguem a maioria; em empate exato, aparece “Conflitante”.</li>
              <li>Critérios só aparecem com 3 ou mais avaliações, para proteger a identidade de quem avaliou.</li>
              <li>Dificuldade e Chamada são neutras; não existe nota geral nem ranking artificial.</li>
            </ul>
          </aside>
        </div>

        {comentarios === null ? (
          <section aria-label="Comentários" className="border-t border-(--border) pt-6">
            <h2 className="text-lg font-semibold">Comentários</h2>
            <p role="alert" className="mt-3 text-sm text-(--ink-soft)">
              Não foi possível carregar os comentários. Recarregue a página para tentar novamente.
            </p>
          </section>
        ) : (
          <SecaoComentarios comentarios={comentarios} />
        )}
      </div>
    </main>
  );
}
