import { nomeUnidade } from "@/lib/unidade";
import { retornoAvaliacaoSeguro } from "@/lib/retorno-avaliacao";
import { consultarAvaliacaoAgregada } from "@/lib/services/avaliacoes";

export default async function DestinoAvaliacao({ retorno }: { retorno: string | null }) {
  const seguro = retornoAvaliacaoSeguro(retorno);
  if (!seguro) return null;
  const partes = seguro.split("?")[0].split("/");
  // Informação pública auxiliar: uma falha não bloqueia a autenticação real.
  const contexto = await consultarAvaliacaoAgregada(partes[2], partes[4]).catch(() => null);
  return (
    <details className="min-w-0 rounded-xl border border-(--border) bg-(--panel)/70 px-4 py-2">
      <summary className="min-h-11 cursor-pointer py-2 text-sm font-medium">Avaliação selecionada</summary>
      {contexto ? <dl className="mt-3 flex flex-col gap-3 break-words text-sm">
        <div><dt className="label-mono">Professor</dt><dd className="font-semibold">{contexto.professor.nome}</dd></div>
        <div><dt className="label-mono">Disciplina</dt><dd className="font-semibold">{contexto.disciplina.nome}</dd></div>
        <div><dt className="label-mono">Código da disciplina</dt><dd className="font-mono">{contexto.disciplina.codigo}</dd></div>
        <div><dt className="label-mono">Unidade acadêmica</dt><dd>{nomeUnidade(contexto.disciplina)}</dd></div>
      </dl> : <p className="mt-3 text-sm text-(--muted)">O destino de retorno foi mantido. Não foi possível carregar seus detalhes agora.</p>}
    </details>
  );
}
