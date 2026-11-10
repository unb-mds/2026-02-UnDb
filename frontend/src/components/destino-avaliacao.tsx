import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";

export default async function DestinoAvaliacao({ retorno }: { retorno: string | null }) {
  const seguro = retornoAvaliacaoSeguro(retorno);
  if (!seguro) return null;
  const partes = seguro.split("?")[0].split("/");
  // Informação pública auxiliar: uma falha não bloqueia a autenticação real.
  const contexto = await consultarAvaliacaoAgregada(partes[2], partes[4]).catch(() => null);
  return (
    <details className="panel min-w-0 p-4 sm:p-5">
      <summary className="min-h-11 cursor-pointer py-2 text-sm font-medium">Avaliação selecionada</summary>
      {contexto ? <dl className="mt-3 flex flex-col gap-3 break-words text-sm">
        <div><dt className="text-(--muted)">Professor</dt><dd className="font-semibold">{contexto.professor.nome}</dd></div>
        <div><dt className="text-(--muted)">Disciplina</dt><dd className="font-semibold">{contexto.disciplina.nome}</dd></div>
        <div><dt className="text-(--muted)">Código da disciplina</dt><dd className="font-mono">{contexto.disciplina.codigo}</dd></div>
        <div><dt className="text-(--muted)">Unidade acadêmica</dt><dd>{contexto.disciplina.departamento}</dd></div>
      </dl> : <p className="mt-3 text-sm text-(--muted)">O destino de retorno foi mantido. Não foi possível carregar seus detalhes agora.</p>}
    </details>
  );
}
