/** Manchas decorativas do protótipo da #211. Só CSS: sem dados, sem foco e paradas com movimento reduzido. */
export default function FundoLiquido() {
  return <div className="liquid-backdrop" aria-hidden="true">
    <div className="liquid-stage">
      {[1, 2, 3, 4, 5].map((n) => <span key={n} className="liquid-blob" />)}
    </div>
  </div>;
}
