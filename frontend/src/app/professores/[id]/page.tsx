import Link from "next/link";
import DisciplinasProfessor from "@/components/disciplinas-professor";
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
        <p className="mt-1 text-sm text-foreground/70">Unidade acadêmica: {professor.departamento}</p>
      </div>

      <div>
        <h2 className="text-sm font-medium text-foreground/70">Disciplinas lecionadas</h2>
        <DisciplinasProfessor professorId={id} disciplinas={disciplinas} />
      </div>
    </main>
  );
}
