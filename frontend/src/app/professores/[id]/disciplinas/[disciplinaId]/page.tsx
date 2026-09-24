import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import type { Dificuldade, QualidadeMaterial } from "@/lib/types/avaliacao";

const MIN_AVALIACOES_EXIBICAO = 3;

const LABEL_DIFICULDADE: Record<Dificuldade, string> = {
  FACIL: "Fácil",
  MEDIO: "Médio",
  DIFICIL: "Difícil",
};

const LABEL_QUALIDADE: Record<QualidadeMaterial, string> = {
  RUIM: "Ruim",
  MEDIO: "Médio",
  BOM: "Bom",
};

function labelBinarioOuConflitante(valor: boolean | "CONFLITANTE", simNao: [string, string]): string {
  if (valor === "CONFLITANTE") return "Conflitante";
  return valor ? simNao[0] : simNao[1];
}

export default async function AvaliacaoAgregadaPage({
  params,
}: {
  params: Promise<{ id: string; disciplinaId: string }>;
}) {
  const { id, disciplinaId } = await params;
  if (!identificadorValido(id) || !identificadorValido(disciplinaId)) notFound();

  const avaliacao = await consultarAvaliacaoAgregada(id, disciplinaId).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href={`/professores/${id}`} className="text-sm text-foreground/60 hover:text-foreground">
        ← Voltar para {avaliacao.professor.nome}
      </Link>

      <div>
        <span className="font-mono text-sm text-foreground/60">{avaliacao.disciplina.codigo}</span>
        <h1 className="text-2xl font-semibold">{avaliacao.professor.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">{avaliacao.disciplina.nome}</p>
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
        <dl className="flex flex-col divide-y divide-foreground/10 rounded-lg border border-foreground/10">
          <div className="flex items-center justify-between px-4 py-3">
            <dt className="text-sm text-foreground/70">Didática</dt>
            <dd className="font-mono text-sm font-medium">{avaliacao.didatica.toFixed(1)} / 5</dd>
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <dt className="text-sm text-foreground/70">Dificuldade</dt>
            <dd className="text-sm font-medium">{LABEL_DIFICULDADE[avaliacao.dificuldade]}</dd>
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <dt className="text-sm text-foreground/70">Faz chamada</dt>
            <dd className="text-sm font-medium">{labelBinarioOuConflitante(avaliacao.chamada, ["Sim", "Não"])}</dd>
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <dt className="text-sm text-foreground/70">Material</dt>
            <dd className="text-sm font-medium">
              {avaliacao.disponibilizaMaterial === "CONFLITANTE"
                ? "Conflitante"
                : avaliacao.disponibilizaMaterial
                  ? avaliacao.qualidadeMaterial
                    ? LABEL_QUALIDADE[avaliacao.qualidadeMaterial]
                    : "Disponibiliza"
                  : "Não disponibiliza"}
            </dd>
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <dt className="text-sm text-foreground/70">Recomenda a matéria</dt>
            <dd className="font-mono text-sm font-medium">{avaliacao.recomenda}%</dd>
          </div>
        </dl>
      )}

      <p className="text-xs text-foreground/50">
        Dificuldade e chamada não indicam algo bom ou ruim — são informativos.
      </p>
      <Link
        href={`/professores/${id}/disciplinas/${disciplinaId}/avaliar`}
        className="self-start rounded-lg bg-accent px-4 py-2.5 font-medium text-white transition hover:opacity-90"
      >
        Avaliar este professor na disciplina
      </Link>
    </main>
  );
}
