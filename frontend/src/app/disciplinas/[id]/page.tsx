import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import {
  compararProfessoresDaDisciplina,
  listarTurmasDaDisciplina,
  obterDisciplina,
} from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import CriteriosAgregados from "@/components/criterios-agregados";
import EtapasJornada from "@/components/etapas-jornada";

export default async function DetalheDisciplinaPage({
  params,
  searchParams,
}: {
  searchParams: Promise<ParametrosBusca>;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const contexto = lerContextoBusca(await searchParams);
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
      <EtapasJornada atual={2} />
      <Link href={contexto ? urlBusca(contexto) : "/disciplinas"} className="self-start text-sm text-accent underline underline-offset-4">
        {contexto ? "← Voltar aos resultados da busca" : "← Buscar outra disciplina"}
      </Link>

      <div className="rounded-xl border border-accent/30 bg-accent/5 p-5 break-words">
        <h1 className="text-2xl font-semibold">{disciplina.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">Código da disciplina: <span className="font-mono">{disciplina.codigo}</span></p>
        <p className="mt-1 text-sm text-foreground/70">Unidade acadêmica: {disciplina.departamento}</p>
      </div>

      <div>
        <h2 className="text-lg font-semibold">Comparação de professores</h2>
        <p className="mt-1 text-sm text-foreground/70">Ordenada pelo percentual de recomendação; desempate por quantidade de avaliações e nome. Dificuldade e Chamada são informações neutras.</p>
        {comparacao.professores.length === 0 ? (
          <p className="mt-2 text-sm text-foreground/60">
            Nenhum professor com turma ativa registrada para esta disciplina no momento.
          </p>
        ) : (
          <ul className="mt-4 grid gap-4 sm:grid-cols-2">
            {comparacao.professores.map((avaliacao) => (
              <li key={avaliacao.professorId} className="min-w-0 rounded-xl border border-foreground/10 p-5 break-words">
                <h3 className="text-lg font-semibold">
                  <Link className="underline-offset-4 hover:underline" href={comContextoBusca(`/professores/${avaliacao.professorId}`, contexto)}>
                    {avaliacao.professor.nome}
                  </Link>
                </h3>
                <p className="text-sm text-foreground/70">Unidade acadêmica: {avaliacao.professor.departamento}</p>
                {avaliacao.dadosSuficientes ? (
                  <CriteriosAgregados avaliacao={avaliacao} />
                ) : (
                  <p className="mt-3 text-sm text-foreground/70">
                    {avaliacao.totalAvaliacoes === 0
                      ? "Sem avaliações registradas."
                      : "Dados insuficientes para exibir os critérios."}
                  </p>
                )}
                <p className="mt-3 text-sm text-foreground/70">{avaliacao.totalAvaliacoes} {avaliacao.totalAvaliacoes === 1 ? "avaliação" : "avaliações"} no total</p>
                <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-sm">
                  <Link
                    className="text-accent underline underline-offset-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                    href={comContextoBusca(`/professores/${avaliacao.professorId}`, contexto)}
                  >
                    Ver disciplinas do professor
                  </Link>
                  <Link
                    className="rounded-lg bg-accent px-4 py-2.5 text-center font-medium text-on-accent hover:opacity-90"
                    href={comContextoBusca(`/professores/${avaliacao.professorId}/disciplinas/${id}/avaliar`, contexto)}
                  >
                    Avaliar nesta disciplina
                  </Link>
                </div>
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
