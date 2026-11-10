import { nomeUnidade } from "@/lib/unidade";
import { lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import DisciplinasProfessor from "@/components/disciplinas-professor";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { listarDisciplinasDoProfessor, obterProfessor } from "@/lib/services/professores";
import { ApiError } from "@/lib/services/http-error";
import Caminho from "@/components/caminho";

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

  // Consultar primeiro o professor mantém o 404 institucional antes das
  // consultas de disciplinas vinculadas.
  const professor = await obterProfessor(id).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });
  const disciplinas = await listarDisciplinasDoProfessor(id);

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-10">
      <Caminho
        itens={[
          { nome: "Início", href: "/" },
          {
            nome: contexto ? "Resultados da busca" : "Professores",
            href: contexto ? urlBusca(contexto) : "/professores",
            retornoBusca: !!contexto,
          },
          { nome: professor.nome },
        ]}
      />
      <Link
        href={contexto ? urlBusca(contexto) : "/professores"}
        className="self-start text-sm text-accent underline underline-offset-4"
      >
        {contexto ? "← Voltar aos resultados da busca" : "← Buscar outro professor"}
      </Link>

      <div className="panel p-6 break-words">
        <h1 className="text-2xl font-bold">{professor.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Unidade acadêmica: {nomeUnidade(professor)}
        </p>
      </div>

      <div>
        <h2 className="text-lg font-semibold">Disciplinas lecionadas</h2>
        <p className="mt-1 text-sm text-foreground/70">
          Escolha a matéria abaixo. Você pode avaliar diretamente ou comparar os professores antes.
        </p>
        <DisciplinasProfessor
          professorId={id}
          disciplinas={disciplinas}
          contexto={contexto}
        />
      </div>
    </main>
  );
}
