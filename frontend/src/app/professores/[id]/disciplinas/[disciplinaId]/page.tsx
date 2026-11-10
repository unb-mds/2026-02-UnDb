import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { listarComentariosPublicados } from "@/lib/services/comentarios";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import CriteriosAgregados from "@/components/criterios-agregados";
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

  const iniciais = avaliacao.professor.nome
    .replace(/^DEMO - /, "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
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

      <div className="flex flex-wrap gap-4 text-sm">
        {contexto && (
          <Link href={urlBusca(contexto)} className="text-accent underline underline-offset-4">
            ← Voltar aos resultados da busca
          </Link>
        )}
        <Link
          href={comContextoBusca(`/professores/${id}`, contexto)}
          className="text-accent underline underline-offset-4"
        >
          ← Voltar para {avaliacao.professor.nome}
        </Link>
      </div>

      <section className="panel profile real-profile">
        <div className="avatar" aria-hidden="true">
          {iniciais || "PR"}
        </div>
        <div className="profile-info">
          <div className="badges">
            <span className="badge blue">{avaliacao.disciplina.codigo}</span>
            <span className="badge">{avaliacao.professor.departamento}</span>
            <span className="badge">{avaliacao.disciplina.departamento}</span>
          </div>
          <h1>{avaliacao.professor.nome}</h1>
          <p className="subtitle">{avaliacao.disciplina.nome}</p>
          <div className="badges">
            <span className="badge outlined">
              {avaliacao.totalAvaliacoes}{" "}
              {avaliacao.totalAvaliacoes === 1 ? "avaliação" : "avaliações"}
            </span>
            <span className="badge">
              {avaliacao.dadosSuficientes
                ? "Dados suficientes (mín. 3)"
                : "Dados insuficientes (mín. 3)"}
            </span>
          </div>
        </div>
        <div className="profile-actions">
          <Link
            className="button primary"
            href={comContextoBusca(`/professores/${id}/disciplinas/${disciplinaId}/avaliar`, contexto)}
          >
            Avaliar este professor na disciplina
          </Link>
          <Link
            className="button"
            href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}
          >
            Comparar professores desta disciplina
          </Link>
          <p>Avaliar exige e-mail institucional confirmado.</p>
        </div>
      </section>

      {!avaliacao.dadosSuficientes ? (
        <div className="panel p-5 text-sm text-foreground/80">
          {avaliacao.totalAvaliacoes === 0 ? (
            <>
              <h2 className="text-base font-semibold text-foreground">Sem avaliações registradas</h2>
              <p className="mt-1 text-foreground/70">
                Ainda não há avaliações para este professor nesta disciplina. A falta de avaliações não significa uma nota baixa — seja o primeiro a avaliar!
              </p>
            </>
          ) : (
            <>
              <h2 className="text-base font-semibold text-foreground">Dados insuficientes para exibir os critérios</h2>
              <p className="mt-1 text-foreground/70">
                Baseado em {avaliacao.totalAvaliacoes} avaliaç{avaliacao.totalAvaliacoes === 1 ? "ão" : "ões"}. São necessárias pelo menos{" "}
                {MIN_AVALIACOES_EXIBICAO} avaliações para proteger o anonimato de quem avaliou. Faltam{" "}
                {MIN_AVALIACOES_EXIBICAO - avaliacao.totalAvaliacoes}.
              </p>
            </>
          )}
        </div>
      ) : (
        <section>
          <div className="section-heading mb-3">
            <h2 className="text-xl font-semibold">Os cinco critérios</h2>
            <p className="text-sm text-foreground/70 mt-1">
              Baseado em {avaliacao.totalAvaliacoes} {avaliacao.totalAvaliacoes === 1 ? "avaliação" : "avaliações"}. Dificuldade e chamada não indicam algo bom ou ruim — são informativos.
            </p>
          </div>
          <CriteriosAgregados avaliacao={avaliacao} />
        </section>
      )}

      <div className="two-columns profile-explanation">
        <section className="panel related">
          <h2>Outros professores desta disciplina</h2>
          {outrosProfessores.length > 0 ? (
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
            <p className="text-sm text-muted mt-2">Nenhum outro professor cadastrado nesta disciplina.</p>
          )}
          <div className="mt-4">
            <Link
              className="text-sm text-accent underline underline-offset-4"
              href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}
            >
              Abrir comparação completa →
            </Link>
          </div>
        </section>

        <aside className="info-panel">
          <h2>Como ler estes números</h2>
          <ul>
            <li>Didática é a média de 1 a 5. Dificuldade e qualidade do material mostram a resposta mais frequente.</li>
            <li>Chamada e disponibilidade de material seguem a maioria; em empate exato, aparece “Conflitante”.</li>
            <li>Critérios só aparecem com 3 ou mais avaliações, para proteger a identidade de quem avaliou.</li>
            <li>Dificuldade e Chamada são neutras; não existe nota geral nem ranking artificial.</li>
          </ul>
        </aside>
      </div>

      {comentarios === null ? (
        <section aria-label="Comentários" className="border-t border-foreground/10 pt-6">
          <h2 className="text-lg font-semibold">Comentários</h2>
          <p role="alert" className="mt-3 text-sm text-foreground/70">
            Não foi possível carregar os comentários. Recarregue a página para tentar novamente.
          </p>
        </section>
      ) : (
        <SecaoComentarios comentarios={comentarios} />
      )}
    </main>
  );
}
