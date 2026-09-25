import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import {
  compararProfessoresDaDisciplina,
  listarTurmasDaDisciplina,
  obterDisciplina,
} from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import type { AvaliacaoAgregadaSuficiente } from "@/lib/types/avaliacao";

const ROTULOS_ENUM = {
  FACIL: "Fácil",
  MEDIO: "Médio",
  DIFICIL: "Difícil",
  RUIM: "Ruim",
  BOM: "Bom",
} as const;

function rotuloEnum(valor: keyof typeof ROTULOS_ENUM): string {
  return ROTULOS_ENUM[valor];
}

function rotuloResposta(valor: boolean | "CONFLITANTE"): string {
  if (valor === "CONFLITANTE") return "Conflitante";
  return valor ? "Sim" : "Não";
}

function rotuloTotalAvaliacoes(total: number): string {
  return `${total} ${total === 1 ? "avaliação" : "avaliações"} no total`;
}

function CriteriosAgregados({ avaliacao }: { avaliacao: AvaliacaoAgregadaSuficiente }) {
  return (
    <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
      <div>
        <dt className="text-foreground/60">Didática</dt>
        <dd className="font-medium">{avaliacao.didatica.toFixed(1)} / 5</dd>
      </div>
      <div>
        <dt className="text-foreground/60">Recomendação</dt>
        <dd className="font-medium">{avaliacao.recomenda}%</dd>
      </div>
      <div>
        <dt className="text-foreground/60">Dificuldade</dt>
        <dd className="font-medium">{rotuloEnum(avaliacao.dificuldade)}</dd>
      </div>
      <div>
        <dt className="text-foreground/60">Faz chamada</dt>
        <dd className="font-medium">{rotuloResposta(avaliacao.chamada)}</dd>
      </div>
      <div>
        <dt className="text-foreground/60">Disponibiliza material</dt>
        <dd className="font-medium">{rotuloResposta(avaliacao.disponibilizaMaterial)}</dd>
      </div>
      <div>
        <dt className="text-foreground/60">Qualidade do material</dt>
        <dd className="font-medium">
          {avaliacao.qualidadeMaterial ? rotuloEnum(avaliacao.qualidadeMaterial) : "Não se aplica"}
        </dd>
      </div>
    </dl>
  );
}

export default async function DetalheDisciplinaPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  if (!identificadorValido(id)) notFound();

  // Sequencial, não Promise.all: mesmo motivo de professores/[id]/page.tsx —
  // o backend consulta a disciplina antes de listar as turmas, então um id
  // inexistente rejeita as duas chamadas, e a segunda escapava do catch da
  // primeira, virando 500 em vez de notFound().
  const disciplina = await obterDisciplina(id).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });
  const [turmas, comparacao] = await Promise.all([
    listarTurmasDaDisciplina(id),
    compararProfessoresDaDisciplina(id),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/disciplinas" className="text-sm text-foreground/60 hover:text-foreground">
        ← Buscar outra disciplina
      </Link>

      <div>
        <span className="font-mono text-sm text-foreground/60">{disciplina.codigo}</span>
        <h1 className="text-2xl font-semibold">{disciplina.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">{disciplina.departamento}</p>
      </div>

      <div>
        <h2 className="text-lg font-semibold">Comparação de professores</h2>
        <p className="mt-1 text-sm text-foreground/60">Ordenada pelo percentual de recomendação.</p>
        {comparacao.professores.length === 0 ? (
          <p className="mt-2 text-sm text-foreground/60">
            Nenhum professor com turma ativa registrada para esta disciplina no momento.
          </p>
        ) : (
          <ul className="mt-3 grid gap-3 sm:grid-cols-2">
            {comparacao.professores.map((avaliacao) => (
              <li key={avaliacao.professorId} className="rounded-lg border border-foreground/10 p-4">
                <h3 className="font-medium">
                  <Link className="underline-offset-4 hover:underline" href={`/professores/${avaliacao.professorId}`}>
                    {avaliacao.professor.nome}
                  </Link>
                </h3>
                <p className="text-sm text-foreground/60">{avaliacao.professor.departamento}</p>
                {avaliacao.dadosSuficientes ? (
                  <CriteriosAgregados avaliacao={avaliacao} />
                ) : (
                  <p className="mt-3 text-sm text-foreground/70">
                    {avaliacao.totalAvaliacoes === 0
                      ? "Sem avaliações registradas."
                      : "Dados insuficientes para exibir os critérios."}
                  </p>
                )}
                <p className="mt-3 text-xs text-foreground/60">{rotuloTotalAvaliacoes(avaliacao.totalAvaliacoes)}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h2 className="text-sm font-medium text-foreground/70">Turmas ativas</h2>
        {turmas.length === 0 ? (
          <p className="mt-2 text-sm text-foreground/60">Nenhuma turma ativa registrada no momento.</p>
        ) : (
          <ul className="mt-2 flex flex-col gap-1 text-sm text-foreground/70">
            {turmas.map((turma) => (
              <li key={turma.id}>
                {turma.semestre} · turma {turma.codigo} ·{" "}
                {turma.professores.length === 0
                  ? "sem docente informado"
                  : turma.professores.map((professor) => professor.nome).join(", ")}
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
