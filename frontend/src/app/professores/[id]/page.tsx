import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { listarDisciplinasDoProfessor, obterProfessor } from "@/lib/services/professores";
import { ApiError } from "@/lib/services/http-error";

export default async function DetalheProfessorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  if (!identificadorValido(id)) notFound();

  // Sequencial, não Promise.all: o backend também consulta o professor antes
  // de listar suas disciplinas, então um id inexistente faz as duas chamadas
  // rejeitarem com 404 — buscando em paralelo, o erro da segunda escapava do
  // catch da primeira e virava 500 em vez de notFound().
  const professor = await obterProfessor(id).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });
  const disciplinas = await listarDisciplinasDoProfessor(id);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href="/professores" className="text-sm text-foreground/60 hover:text-foreground">
        ← Buscar outro professor
      </Link>

      <div>
        <h1 className="text-2xl font-semibold">{professor.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">{professor.departamento}</p>
      </div>

      <div>
        <h2 className="text-sm font-medium text-foreground/70">Disciplinas lecionadas</h2>
        {disciplinas.length === 0 ? (
          <p className="mt-2 text-sm text-foreground/60">
            Nenhuma turma ativa registrada para este professor no momento.
          </p>
        ) : (
          <ul className="mt-2 flex flex-col gap-2">
            {disciplinas.map((disciplina) => (
              <li
                key={disciplina.id}
                className="rounded-lg border border-foreground/10 px-4 py-3 transition hover:border-foreground/30 hover:bg-foreground/[0.03]"
              >
                <Link href={`/professores/${id}/disciplinas/${disciplina.id}`} className="block">
                  <span className="font-mono text-xs text-foreground/60">{disciplina.codigo}</span>
                  <span className="block font-medium">{disciplina.nome}</span>
                </Link>
                <Link
                  href={`/disciplinas/${disciplina.id}`}
                  className="mt-1 inline-block text-xs text-foreground/60 underline underline-offset-2 hover:text-foreground"
                >
                  Ver outros professores desta disciplina →
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
