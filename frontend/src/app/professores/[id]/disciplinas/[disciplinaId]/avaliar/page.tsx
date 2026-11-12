import { nomeUnidade } from "@/lib/unidade";
import { comContextoBusca, lerContextoBusca, urlBusca, type ParametrosBusca } from "@/lib/contexto-busca";
import Link from "next/link";
import { notFound } from "next/navigation";
import { identificadorValido } from "@/lib/identificador";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import { caminhoAvaliacao } from "@/lib/retorno-avaliacao";
import AvaliacaoForm from "./avaliacao-form";
import Caminho from "@/components/caminho";
import FundoLiquido from "@/components/fundo-liquido";
import Icone from "@/components/icone";

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
    <main className="relative isolate flex flex-1 flex-col overflow-hidden">
      <FundoLiquido />
      <div className="container flex max-w-[928px]! min-w-0 flex-col gap-6 py-8 sm:py-12">
        <Caminho itens={[{ nome: "Início", href: "/" }, ...(contexto ? [{ nome: "Resultados", href: urlBusca(contexto), retornoBusca: true }] : []), { nome: "Consulta", href: consultaHref }, { nome: "Avaliar" }]} />
        <div className="-mt-2 flex flex-wrap gap-x-6">
          {contexto && <Link href={urlBusca(contexto)} className="back-link"><Icone nome="arrow-left" pequeno /> Voltar aos resultados da busca</Link>}
          <Link href={consultaHref} className="back-link"><Icone nome="arrow-left" pequeno /> Voltar para a consulta</Link>
        </div>
        <div>
          <span className="kicker">Sua experiência</span>
          <h1 className="page-title mt-2">Avaliar professor na disciplina</h1>
          <p className="lead mt-2">Confira o contexto e responda aos cinco critérios. Suas respostas serão exibidas apenas de forma agregada.</p>
        </div>
        {avaliacao ? (
          <>
            <dl className="grid min-w-0 gap-5 rounded-2xl border-l-2 border-accent bg-(--surface-accent)/70 p-4 break-words sm:grid-cols-3 sm:p-5">
              <div>
                <dt className="kicker text-(--ink-soft)!">Professor</dt>
                <dd className="mt-1 font-medium">{avaliacao.professor.nome}</dd>
              </div>
              <div>
                <dt className="kicker text-(--ink-soft)!">Disciplina</dt>
                <dd className="mt-1 font-medium">
                  <span className="block">{avaliacao.disciplina.nome}</span>
                  <span className="mt-1 block text-sm font-normal text-(--ink-soft)">
                    Código da disciplina: <span className="font-mono">{avaliacao.disciplina.codigo}</span>
                  </span>
                </dd>
              </div>
              <div>
                <dt className="kicker text-(--ink-soft)!">Unidade acadêmica</dt>
                <dd className="mt-1 font-medium">{nomeUnidade(avaliacao.disciplina)}</dd>
              </div>
            </dl>
            <AvaliacaoForm professorId={avaliacao.professorId} disciplinaId={avaliacao.disciplinaId} retornoHref={retornoHref} />
          </>
        ) : (
          <p role="alert" className="status-box error">
            Não foi possível carregar o professor e a disciplina. Tente recarregar esta página em instantes.
          </p>
        )}
      </div>
    </main>
  );
}
