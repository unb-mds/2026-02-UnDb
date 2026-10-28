import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import { caminhoAvaliacao } from "@/lib/retorno-avaliacao";
import AvaliacaoForm from "./avaliacao-form";

export default async function AvaliarPage({ params, searchParams }: {
  searchParams: Promise<ParametrosBusca>;
  params: Promise<{ id: string; disciplinaId: string }>;
}) {
  const { id, disciplinaId } = await params;
  const contexto = lerContextoBusca(await searchParams);
  if (!identificadorValido(id) || !identificadorValido(disciplinaId)) notFound();
  const consultaHref = comContextoBusca(`/professores/${id}/disciplinas/${disciplinaId}`, contexto);
  const retornoHref = comContextoBusca(caminhoAvaliacao(id, disciplinaId), contexto);
  const avaliacao = await consultarAvaliacaoAgregada(id, disciplinaId).catch((erro) => {
    if (erro instanceof ApiError && erro.naoEncontrado) notFound();
    return null;
  });

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
      {contexto && <Link href={urlBusca(contexto)} className="text-sm text-accent underline underline-offset-4">← Voltar aos resultados da busca</Link>}
      <Link href={consultaHref} className="text-sm text-foreground/60 hover:text-foreground">
        ← Voltar para a consulta
      </Link>
      <div>
        <h1 className="text-2xl font-semibold">Avaliar professor na disciplina</h1>
        <p className="mt-1 text-sm text-foreground/70">Confira o contexto e responda aos cinco critérios.</p>
      </div>
      {avaliacao ? (
        <>
          <dl className="flex flex-col gap-3 rounded-lg border border-foreground/10 px-4 py-3">
            <div>
              <dt className="text-sm text-foreground/70">Professor</dt>
              <dd className="font-semibold">{avaliacao.professor.nome}</dd>
            </div>
            <div>
              <dt className="text-sm text-foreground/70">Disciplina</dt>
              <dd className="font-medium">
                <span className="block">{avaliacao.disciplina.nome}</span>
                <span className="mt-1 block text-sm font-normal text-foreground/70">
                  Código da disciplina: <span className="font-mono">{avaliacao.disciplina.codigo}</span>
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm text-foreground/70">Unidade acadêmica</dt>
              <dd className="font-medium">{avaliacao.disciplina.departamento}</dd>
            </div>
          </dl>
          <AvaliacaoForm professorId={avaliacao.professorId} disciplinaId={avaliacao.disciplinaId} retornoHref={retornoHref} />
        </>
      ) : (
        <p role="alert" className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">
          Não foi possível carregar o professor e a disciplina. Tente recarregar esta página em instantes.
        </p>
      )}
    </main>
  );
}
