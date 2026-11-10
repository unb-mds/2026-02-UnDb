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
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-10">
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

      <div className="rounded-xl border border-accent/30 bg-accent/5 p-5 break-words">
        <h1 className="text-2xl font-semibold">{disciplina.nome}</h1>
        <p className="mt-1 text-sm text-foreground/70">
          Código da disciplina: <span className="font-mono">{disciplina.codigo}</span>
        </p>
        <p className="mt-1 text-sm text-foreground/70">
          Unidade acadêmica: {nomeUnidade(disciplina)}
        </p>
      </div>

      <div className="flex flex-wrap gap-4 text-sm">
        {contexto ? (
          <Link href={urlBusca(contexto)} className="text-accent underline underline-offset-4">
            ← Voltar aos resultados da busca
          </Link>
        ) : (
          <Link href="/disciplinas" className="text-accent underline underline-offset-4">
            ← Buscar outra disciplina
          </Link>
        )}
      </div>

      <ComparacaoDark
        professores={comparacao.professores}
        disciplinaId={id}
        contexto={contexto}
        turmas={turmas}
      />

      <details className="panel institutional-details mt-6">
        <summary>Turmas ativas e ofertas ({turmas.length})</summary>
        {turmas.length === 0 ? (
          <p className="text-sm text-foreground/60">
            Nenhuma turma ativa registrada no momento.
          </p>
        ) : (
          <ul className="flex flex-col gap-1 text-sm text-foreground/70 list-disc">
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
    </main>
  );
}
