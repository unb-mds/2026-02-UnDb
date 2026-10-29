import { lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import DisciplinasProfessor from "@/components/disciplinas-professor";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { listarDisciplinasDoProfessor, obterProfessor } from "@/lib/services/professores";
import { ApiError } from "@/lib/services/http-error";
import EtapasJornada from "@/components/etapas-jornada";

export default async function DetalheProfessorPage({
  params,
  searchParams,
}: {
  searchParams: Promise<ParametrosBusca>;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const contexto = lerContextoBusca(await searchParams);
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
      <EtapasJornada atual={1} />
      <Link href={contexto ? urlBusca(contexto) : "/professores"} className="self-start text-sm text-accent underline underline-offset-4">
        {contexto ? "← Voltar aos resultados da busca" : "← Buscar outro professor"}
      </Link>

      <div className="rounded-xl border border-accent/30 bg-accent/5 p-5 break-words">
        <h1 className="text-2xl font-semibold">{professor.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">Unidade acadêmica: {professor.departamento}</p>
      </div>

      <div>
        <h2 className="text-sm font-medium text-foreground/70">Disciplinas lecionadas</h2>
        <p className="mt-2 text-sm text-foreground/70">Escolha a matéria abaixo. Você pode avaliar diretamente ou comparar os professores antes.</p>
        <DisciplinasProfessor professorId={id} disciplinas={disciplinas} contexto={contexto} />
      </div>
    </main>
  );
}
