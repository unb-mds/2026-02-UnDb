import Link from "next/link";
import { notFound } from "next/navigation";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import AvaliacaoForm from "./avaliacao-form";

export default async function AvaliarPage({ params }: {
  params: Promise<{ id: string; disciplinaId: string }>;
}) {
  const { id, disciplinaId } = await params;
  const consultaHref = `/professores/${id}/disciplinas/${disciplinaId}`;
  const avaliacao = await consultarAvaliacaoAgregada(id, disciplinaId).catch((erro) => {
    if (erro instanceof ApiError && (erro.status === 404 || erro.status === 422)) notFound();
    return null;
  });

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      <Link href={consultaHref} className="text-sm text-foreground/60 hover:text-foreground">
        ← Voltar para a consulta
      </Link>
      <h1 className="text-2xl font-semibold">Avaliar professor na disciplina</h1>
      {avaliacao ? (
        <>
          <dl className="flex flex-col gap-3 rounded-lg border border-foreground/10 px-4 py-3">
            <div>
              <dt className="text-sm text-foreground/70">Professor</dt>
              <dd className="font-medium">{avaliacao.professor.nome}</dd>
            </div>
            <div>
              <dt className="text-sm text-foreground/70">Disciplina</dt>
              <dd><span className="font-mono text-sm">{avaliacao.disciplina.codigo}</span> — {avaliacao.disciplina.nome}</dd>
            </div>
          </dl>
          <AvaliacaoForm professorId={avaliacao.professorId} disciplinaId={avaliacao.disciplinaId} />
        </>
      ) : (
        <p role="alert" className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">
          Não foi possível carregar o professor e a disciplina. Tente recarregar esta página em instantes.
        </p>
      )}
    </main>
  );
}
