import { nomeUnidade } from "@/lib/unidade";
import { lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import {
  compararProfessoresDaDisciplina,
  listarTurmasDaDisciplina,
  obterDisciplina,
} from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import ComparacaoDark from "@/components/comparacao-dark";
import Caminho from "@/components/caminho";
import FundoParticulas from "@/components/fundo-particulas";
import Icone from "@/components/icone";

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

  // Consultar primeiro a disciplina faz com que um ID inexistente vire 404
  // antes das consultas dependentes de turmas e agregados.
  const disciplina = await obterDisciplina(id).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    throw erro;
  });
  const [turmas, comparacao] = await Promise.all([
    listarTurmasDaDisciplina(id),
    compararProfessoresDaDisciplina(id),
  ]);

  return (
    <main className="relative isolate flex flex-1 flex-col overflow-hidden">
      <FundoParticulas />
      <div className="container flex flex-col gap-8 py-8 sm:py-12">
        <Caminho
          itens={[
            { nome: "Início", href: "/" },
            {
              nome: contexto ? "Resultados da busca" : "Disciplinas",
              href: contexto ? urlBusca(contexto) : "/disciplinas",
              retornoBusca: !!contexto,
            },
            { nome: disciplina.codigo },
            { nome: "Comparar professores" },
          ]}
        />

        <header className="flex flex-wrap items-start justify-between gap-4 break-words">
          <div className="flex max-w-3xl flex-col items-start gap-3">
            <span className="code-chip"><span className="sr-only">Código da disciplina: </span>{disciplina.codigo}</span>
            <h1 className="page-title">{disciplina.nome}</h1>
            <p className="lead">Unidade acadêmica: {nomeUnidade(disciplina)}</p>
          </div>
          {contexto ? (
            <Link href={urlBusca(contexto)} className="back-link">
              <Icone nome="arrow-left" pequeno /> Voltar aos resultados da busca
            </Link>
          ) : (
            <Link href="/disciplinas" className="back-link">
              <Icone nome="arrow-left" pequeno /> Buscar outra disciplina
            </Link>
          )}
        </header>

        <ComparacaoDark
          professores={comparacao.professores}
          disciplinaId={id}
          contexto={contexto}
          turmas={turmas}
        />

        <details className="glass institutional-details rounded-2xl!">
          <summary>Turmas ativas e ofertas ({turmas.length})</summary>
          {turmas.length === 0 ? (
            <p className="text-sm text-(--ink-soft)">
              Nenhuma turma ativa registrada no momento.
            </p>
          ) : (
            <ul className="flex flex-col gap-1 text-sm text-(--ink-soft) list-disc">
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
        </details>
      </div>
    </main>
  );
}
