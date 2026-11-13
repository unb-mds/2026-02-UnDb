import type { CSSProperties } from "react";
import EstrelasDidatica, { formatarDidatica } from "./estrelas-didatica";

export type CriterioInformativo = { rotulo: string; valor: string; legenda: string };

/**
 * Apresenta os critérios já agregados pelo backend lado a lado, sem nota geral.
 * Recomendação e Didática ficam em destaque próprio; os demais são informativos e neutros.
 */
export default function ResultadoBento({ rotulo, recomenda, didatica, total, criterios }: {
  rotulo: string;
  recomenda: number;
  didatica: number;
  total: number;
  criterios: CriterioInformativo[];
}) {
  const respostas = `${total} ${total === 1 ? "resposta" : "respostas"}`;
  return <dl className="bento" aria-label={rotulo}>
    <div className="bento-card bento-primary">
      <dt className="bento-chip w-fit">Recomendação</dt>
      <dd className="bento-value -mt-3">{recomenda}%</dd>
      <dd className="mt-auto grid gap-3">
        <span className="bento-caption">recomendam este professor nesta disciplina</span>
        <span className="meter" aria-hidden="true"><span style={{ width: `${recomenda}%` } as CSSProperties} /></span>
      </dd>
    </div>
    <div className="bento-card bento-wide grid! grid-cols-[minmax(0,1fr)_auto] gap-x-6 gap-y-1 max-[480px]:grid-cols-1">
      <dt className="label-mono">Didática</dt>
      <dd className="col-start-2 row-span-3 row-start-1 self-center max-[480px]:order-last max-[480px]:col-start-1 max-[480px]:row-span-1 max-[480px]:row-start-auto max-[480px]:mt-2"><EstrelasDidatica valor={didatica} /></dd>
      <dd className="bento-wide-value">{formatarDidatica(didatica)}<small>/5</small></dd>
      <dd className="bento-caption">Média de {respostas}</dd>
    </div>
    {criterios.map((criterio) => <div key={criterio.rotulo} className="bento-card bento-tile">
      <dt className="label-mono order-2">{criterio.rotulo}</dt>
      <dd className="bento-tile-value order-1">{criterio.valor}</dd>
      <dd className="bento-caption order-3">{criterio.legenda}</dd>
    </div>)}
  </dl>;
}
