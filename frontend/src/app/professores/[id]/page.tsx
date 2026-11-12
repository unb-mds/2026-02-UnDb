import { nomeUnidade } from "@/lib/unidade";
import { lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { iniciaisProfessor } from "@/lib/iniciais";
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
    <main className="container flex max-w-[928px]! flex-1 flex-col gap-6 py-8 sm:py-12">
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
        className="back-link"
      >
        {contexto ? "← Voltar aos resultados da busca" : "← Buscar outro professor"}
      </Link>

      <div className="flex min-w-0 items-center gap-5 break-words">
        <span className="avatar-initials large" aria-hidden="true">{iniciaisProfessor(professor.nome)}</span>
        <div className="min-w-0">
        <span className="kicker">Professor</span>
        <h1 className="page-title mt-1">{professor.nome}</h1>
        <p className="lead mt-2">
          Unidade acadêmica: {nomeUnidade(professor)}
        </p>
        </div>
      </div>

      <div>
        <h2 className="section-title">Disciplinas lecionadas</h2>
        <p className="mt-2 text-sm text-(--ink-soft)">
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
