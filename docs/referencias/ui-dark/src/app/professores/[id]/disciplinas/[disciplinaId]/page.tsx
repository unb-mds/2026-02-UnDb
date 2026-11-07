import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import Caminho from "@/components/caminho";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { listarComentariosPublicados } from "@/lib/services/comentarios";
import { ApiError } from "@/lib/services/http-error";
import CriteriosAgregados from "@/components/criterios-agregados";
import SecaoComentarios from "@/components/secao-comentarios";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";

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

  const [comentarios, comparacao] = await Promise.all([listarComentariosPublicados(id, disciplinaId).catch(() => null), compararProfessoresDaDisciplina(disciplinaId).catch(() => null)]);

  return (
    <main className="mx-auto flex w-full max-w-5xl dark-profile flex-1 flex-col gap-6 px-4 py-10">
      <Caminho itens={[{ nome: "Início", href: "/" }, { nome: contexto ? "Resultados da busca" : "Professores", href: contexto ? urlBusca(contexto) : "/professores", retornoBusca: !!contexto }, { nome: avaliacao.disciplina.codigo, href: comContextoBusca(`/disciplinas/${disciplinaId}`, contexto) }, { nome: avaliacao.professor.nome }]} />

      <section className="panel profile real-profile">
        <div className="avatar" aria-hidden="true">{avaliacao.professor.nome.replace(/^DEMO - /, "").split(" ").filter(Boolean).slice(0,2).map(p => p[0]).join("")}</div>
        <div className="profile-info"><div className="badges"><span className="badge blue">{avaliacao.disciplina.codigo}</span><span className="badge">{avaliacao.professor.departamento}</span></div>
          <h1>{avaliacao.professor.nome}</h1><p className="subtitle">{avaliacao.disciplina.nome}</p>
          <div className="badges"><span className="badge outlined">{avaliacao.totalAvaliacoes} avaliações simuladas</span><span className="badge">{avaliacao.dadosSuficientes ? "Dados suficientes (mín. 3)" : "Dados insuficientes (mín. 3)"}</span></div>
        </div><div className="profile-actions"><Link className="button primary" href={comContextoBusca(`/professores/${id}/disciplinas/${disciplinaId}/avaliar`, contexto)}>Avaliar este professor</Link><Link className="button" href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}>Comparar professores</Link><p>Avaliar exige e-mail institucional confirmado.</p></div>
      </section>

      {!avaliacao.dadosSuficientes ? (
        <div className="rounded-lg border border-foreground/10 px-4 py-3 text-sm text-foreground/70">
          Dados insuficientes para exibir os critérios — são necessárias pelo menos{" "}
          {MIN_AVALIACOES_EXIBICAO} avaliações para proteger a identidade de quem avaliou.
          {avaliacao.totalAvaliacoes > 0 && (
            <> Faltam {MIN_AVALIACOES_EXIBICAO - avaliacao.totalAvaliacoes}.</>
          )}
        </div>
      ) : (
        <section><div className="section-heading"><h2>Os cinco critérios</h2></div><CriteriosAgregados avaliacao={avaliacao} /></section>
      )}

      <p className="text-sm text-foreground/70">
        Dificuldade e chamada não indicam algo bom ou ruim — são informativos.
      </p>
      <div className="two-columns profile-explanation"><section className="panel related"><h2>Outros professores desta disciplina</h2>{comparacao ? comparacao.professores.filter(p => p.professorId !== id).map(p => <Link key={p.professorId} className="related-row" href={comContextoBusca(`/professores/${p.professorId}/disciplinas/${disciplinaId}`, contexto)}><span>{p.professor.nome}<small>{p.totalAvaliacoes} avaliações</small></span><span className={p.dadosSuficientes ? "code" : "muted"}>{p.dadosSuficientes ? `${p.recomenda}% recomendam` : "Dados insuficientes"}</span></Link>) : <Link className="text-link" href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}>Abrir comparação →</Link>}</section><aside className="info-panel"><h2>Como ler estes números</h2><ul><li>Didática é a média de 1 a 5. Dificuldade e qualidade do material mostram a resposta mais frequente.</li><li>Chamada e disponibilidade de material seguem a maioria; em empate exato, aparece “Conflitante”.</li><li>Critérios só aparecem com 3 ou mais avaliações, para proteger quem avaliou.</li></ul></aside></div>

      {comentarios === null ? (
        <section aria-label="Comentários" className="border-t border-foreground/10 pt-6">
          <h2 className="text-lg font-semibold">Comentários</h2>
          <p role="alert" className="mt-3 text-sm text-foreground/70">
            Não foi possível carregar os comentários. Recarregue a página para tentar novamente.
          </p>
        </section>
      ) : <SecaoComentarios comentarios={comentarios} />}
    </main>
  );
}
