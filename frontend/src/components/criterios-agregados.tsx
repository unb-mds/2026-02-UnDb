import type { AvaliacaoAgregadaSuficiente } from "@/lib/types/avaliacao";

const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", RUIM: "Ruim", BOM: "Bom" } as const;

// Apresenta os valores já agregados pelo backend; não recalcula critérios.
export default function CriteriosAgregados({ avaliacao }: { avaliacao: AvaliacaoAgregadaSuficiente }) {
  const material = avaliacao.disponibilizaMaterial === "CONFLITANTE" ? "Conflitante"
    : !avaliacao.disponibilizaMaterial ? "Não disponibiliza"
    : avaliacao.qualidadeMaterial ? rotulos[avaliacao.qualidadeMaterial] : "Disponibiliza";
  const criterios = [
    ["Didática", `${avaliacao.didatica.toFixed(1)} / 5`],
    ["Dificuldade", rotulos[avaliacao.dificuldade]],
    ["Faz chamada", avaliacao.chamada === "CONFLITANTE" ? "Conflitante" : avaliacao.chamada ? "Sim" : "Não"],
    ["Material", material],
    ["Recomenda a matéria", `${avaliacao.recomenda}%`],
  ];
  return <dl className="mt-4 flex flex-col divide-y divide-foreground/10">
    {criterios.map(([rotulo, valor]) => <div key={rotulo} className="flex flex-wrap justify-between gap-x-4 gap-y-1 py-2 text-sm">
      <dt className="text-foreground/70">{rotulo}</dt><dd className="font-medium">{valor}</dd>
    </div>)}
  </dl>;
}
