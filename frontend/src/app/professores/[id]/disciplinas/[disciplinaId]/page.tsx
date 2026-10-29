import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import CriteriosAgregados from "@/components/criterios-agregados";
import EtapasJornada from "@/components/etapas-jornada";

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

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <EtapasJornada atual={2} />
      {contexto && <Link href={urlBusca(contexto)} className="text-sm text-accent underline underline-offset-4">← Voltar aos resultados da busca</Link>}
      <Link href={comContextoBusca(`/professores/${id}`, contexto)} className="self-start text-sm text-accent underline underline-offset-4">
        ← Voltar para {avaliacao.professor.nome}
      </Link>

      <div className="rounded-xl border border-accent/30 bg-accent/5 p-5 break-words">
        <h1 className="text-2xl font-semibold">{avaliacao.professor.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">Unidade acadêmica do professor: {avaliacao.professor.departamento}</p>
        <p className="mt-3 font-medium">{avaliacao.disciplina.nome}</p>
        <p className="text-sm text-foreground/70">Código da disciplina: <span className="font-mono">{avaliacao.disciplina.codigo}</span></p>
        <p className="text-sm text-foreground/70">Unidade acadêmica: {avaliacao.disciplina.departamento}</p>
      </div>

      <p className="text-sm text-foreground/70">
        {avaliacao.totalAvaliacoes === 0
          ? "Ainda não há avaliações para este professor nesta disciplina."
          : `Baseado em ${avaliacao.totalAvaliacoes} avaliaç${avaliacao.totalAvaliacoes === 1 ? "ão" : "ões"}.`}
      </p>

      {!avaliacao.dadosSuficientes ? (
        <div className="rounded-lg border border-foreground/10 px-4 py-3 text-sm text-foreground/70">
          Dados insuficientes para exibir os critérios — são necessárias pelo menos{" "}
          {MIN_AVALIACOES_EXIBICAO} avaliações para proteger a identidade de quem avaliou.
          {avaliacao.totalAvaliacoes > 0 && (
            <> Faltam {MIN_AVALIACOES_EXIBICAO - avaliacao.totalAvaliacoes}.</>
          )}
        </div>
      ) : (
        <div className="rounded-xl border border-foreground/10 p-5"><CriteriosAgregados avaliacao={avaliacao} /></div>
      )}

      <p className="text-sm text-foreground/70">
        Dificuldade e chamada não indicam algo bom ou ruim — são informativos.
      </p>
      <Link
        href={comContextoBusca(`/professores/${id}/disciplinas/${disciplinaId}/avaliar`, contexto)}
        className="self-start rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent transition hover:opacity-90"
      >
        Avaliar este professor na disciplina
      </Link>
      <Link
        href={comContextoBusca(`/disciplinas/${disciplinaId}`, contexto)}
        className="self-start text-sm text-accent underline underline-offset-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Comparar professores desta disciplina
      </Link>
    </main>
  );
}
