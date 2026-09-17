import Link from "next/link";
import { notFound } from "next/navigation";
import { listarTurmasDaDisciplina, obterDisciplina } from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import type { ProfessorDetalhe } from "@/lib/types/institucional";

export default async function DetalheDisciplinaPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Sequencial, não Promise.all: mesmo motivo de professores/[id]/page.tsx —
  // o backend consulta a disciplina antes de listar as turmas, então um id
  // inexistente rejeita as duas chamadas, e a segunda escapava do catch da
  // primeira, virando 500 em vez de notFound().
  const disciplina = await obterDisciplina(id).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });
  const turmas = await listarTurmasDaDisciplina(id);

  const professores = new Map<string, ProfessorDetalhe>();
  for (const turma of turmas) {
    for (const professor of turma.professores) {
      professores.set(professor.id, professor);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/disciplinas" className="text-sm text-foreground/60 hover:text-foreground">
        ← Buscar outra disciplina
      </Link>

      <div>
        <span className="font-mono text-sm text-foreground/60">{disciplina.codigo}</span>
        <h1 className="text-2xl font-semibold">{disciplina.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">{disciplina.departamento}</p>
      </div>

      <div>
        <h2 className="text-sm font-medium text-foreground/70">Professores que lecionam esta disciplina</h2>
        {professores.size === 0 ? (
          <p className="mt-2 text-sm text-foreground/60">
            Nenhum professor com turma ativa registrada para esta disciplina no momento.
          </p>
        ) : (
          <ul className="mt-2 flex flex-col gap-2">
            {Array.from(professores.values()).map((professor) => (
              <li key={professor.id}>
                <Link
                  href={`/professores/${professor.id}`}
                  className="block rounded-lg border border-foreground/10 px-4 py-3 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
                >
                  <span className="font-medium">{professor.nome}</span>
                  <span className="block text-sm text-foreground/60">{professor.departamento}</span>
                </Link>
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
