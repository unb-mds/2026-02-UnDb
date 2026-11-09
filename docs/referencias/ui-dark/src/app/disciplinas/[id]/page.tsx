import { lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Caminho from "@/components/caminho";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import {
  compararProfessoresDaDisciplina,
  listarTurmasDaDisciplina,
  obterDisciplina,
} from "@/lib/services/disciplinas";
import { ApiError } from "@/lib/services/http-error";
import ComparacaoDark from "@/components/comparacao-dark";

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
      <Caminho itens={[{ nome: "Início", href: "/" }, { nome: contexto ? "Resultados da busca" : "Disciplinas", href: contexto ? urlBusca(contexto) : "/disciplinas", retornoBusca: !!contexto }, { nome: disciplina.codigo }, { nome: "Comparar professores" }]} />

      <div className="comparison-heading"><div><div className="badges"><span className="badge blue">{disciplina.codigo}</span><span className="badge">{disciplina.departamento}</span></div><h1>Quem ensina {disciplina.nome}</h1></div></div>

      <ComparacaoDark professores={comparacao.professores} disciplinaId={id} contexto={contexto} turmas={turmas} />

      <details className="panel institutional-details"><summary>Turmas ativas e ofertas</summary>
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
      </details>
    </main>
  );
}
