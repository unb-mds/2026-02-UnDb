import type { AvaliacaoAgregadaSuficiente } from "@/lib/types/avaliacao";

const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", RUIM: "Ruim", BOM: "Bom" } as const;

// Apresenta os valores já agregados pelo backend; não recalcula critérios.
export default function CriteriosAgregados({ avaliacao }: { avaliacao: AvaliacaoAgregadaSuficiente }) {
  const material = avaliacao.disponibilizaMaterial === "CONFLITANTE" ? "Conflitante"
    : !avaliacao.disponibilizaMaterial ? "Não disponibiliza"
    : avaliacao.qualidadeMaterial ? `Sim · ${rotulos[avaliacao.qualidadeMaterial]}` : "Disponibiliza";
  const criterios = [
    ["Didática", `${avaliacao.didatica.toLocaleString("pt-BR", {minimumFractionDigits:1})} / 5`, `média de ${avaliacao.totalAvaliacoes} avaliações`],
    ["Dificuldade", rotulos[avaliacao.dificuldade], "resposta mais frequente"],
    ["Faz chamada", avaliacao.chamada === "CONFLITANTE" ? "Conflitante" : avaliacao.chamada ? "Sim" : "Não", "maioria das respostas"],
    ["Material", material, "disponibilidade e qualidade"],
    ["Recomenda a matéria", `${avaliacao.recomenda}%`, "recomendam a matéria"],
  ];
  return <dl className="metrics">
    {criterios.map(([rotulo, valor, nota]) => <div key={rotulo} className="panel metric">
      <div className="metric-dash" /><dt>{rotulo}</dt><dd>{valor}</dd><p>{nota}</p>
    </div>)}
  </dl>;
}
