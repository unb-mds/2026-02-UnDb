"use client";

import { useState } from "react";
import { criteriosAvaliacao } from "@/lib/avaliacao-formulario";
import Icone from "./icone";

type Criterio = (typeof criteriosAvaliacao)[number];

const PERGUNTAS: Record<Criterio["nome"], { pergunta: string; dica?: string }> = {
  didatica: { pergunta: "Como você avalia a didática?" },
  dificuldade: { pergunta: "Qual foi a dificuldade da disciplina?", dica: "Este critério é informativo, não positivo ou negativo." },
  chamada: { pergunta: "O professor faz chamada?", dica: "Este critério é informativo, não positivo ou negativo." },
  material: { pergunta: "Como é o material disponibilizado?", dica: "Como slides, listas ou referências. Escolha “Não disponibiliza” se não houve material." },
  recomenda: { pergunta: "Você recomendaria este professor nesta disciplina?" },
};

function Opcao({ nome, valor, rotulo, checked, onChange }: {
  nome: string; valor: string; rotulo: string; checked?: boolean; onChange?: () => void;
}) {
  return <label className="choice">
    <input type="radio" name={nome} value={valor} required checked={checked} onChange={onChange} />
    <span>{rotulo}<Icone nome="check" pequeno /></span>
  </label>;
}

function Cabecalho({ numero, titulo, texto }: { numero: string; titulo: string; texto: string }) {
  return <legend className="mb-2 flex w-full items-start gap-3">
    <span className="form-step" aria-hidden="true">{numero}</span>
    <span className="flex flex-col gap-1">
      <span className="text-xl font-medium sm:text-2xl">{titulo}</span>
      <span className="text-sm text-(--ink-soft)">{texto}</span>
    </span>
  </legend>;
}

export default function CriteriosAvaliacao({ disabled = false, onChange, rotulosExplicitos = false, ocultarDidatica = false }: {
  disabled?: boolean;
  onChange?: () => void;
  rotulosExplicitos?: boolean;
  ocultarDidatica?: boolean;
  /** Mantido por compatibilidade: a didática já abre a seção em destaque. */
  destacarDidatica?: boolean;
}) {
  const [didatica, setDidatica] = useState("");
  const criterioDidatica = criteriosAvaliacao[0];
  const demaisCriterios = criteriosAvaliacao.slice(1);

  function alterarDidatica(valor: string) {
    setDidatica(valor);
    onChange?.();
  }

  function rotuloOpcao(criterio: Criterio, valor: string, rotulo: string) {
    if (criterio.nome === "recomenda" && rotulosExplicitos) return valor === "true" ? "Recomendo" : "Não recomendo";
    if (criterio.nome === "chamada" && rotulosExplicitos) return valor === "true" ? "Faz chamada" : "Não faz chamada";
    return rotulo;
  }

  // Função de renderização (não componente) para não remontar os rádios não controlados.
  function grupo(criterio: Criterio) {
    const { pergunta, dica } = PERGUNTAS[criterio.nome];
    const dicaId = `criterio-${criterio.nome}-dica`;
    return <fieldset key={criterio.nome} className="flex min-w-0 flex-col gap-3 border-t border-(--border) pt-5" aria-describedby={dica ? dicaId : undefined}>
      <legend className="pr-3 text-base font-medium">{rotulosExplicitos ? pergunta : criterio.rotulo}</legend>
      {dica && <p id={dicaId} className="text-sm text-(--muted)">{dica}</p>}
      <div className={`choice-grid ${criterio.opcoes.length === 2 ? "two" : ""}`}>
        {criterio.opcoes.map(([valor, rotulo]) => <Opcao key={valor} nome={criterio.nome} valor={valor} rotulo={rotuloOpcao(criterio, valor, rotulo)} onChange={onChange} />)}
      </div>
    </fieldset>;
  }

  const recomendacao = demaisCriterios.find((criterio) => criterio.nome === "recomenda");

  return (
    <div className="flex min-w-0 flex-col gap-5">
      <div className="glass rounded-2xl! p-3 sm:p-6"><fieldset disabled={disabled} className="flex min-w-0 flex-col gap-5">
        <Cabecalho numero="01" titulo="Sobre as aulas" texto="Selecione uma opção em cada critério." />

        {!ocultarDidatica && (
          <fieldset className="flex min-w-0 flex-col gap-3 border-t border-(--border) pt-5">
            <legend className="pr-3 text-base font-medium">{rotulosExplicitos ? PERGUNTAS.didatica.pergunta : "Didática"}</legend>
            <div className="grid grid-cols-5 gap-1 min-[375px]:gap-2.5" aria-label="Nota de Didática">
              {criterioDidatica.opcoes.map(([valor, rotulo]) => (
                <Opcao key={valor} nome="didatica" valor={valor} rotulo={rotulo} checked={didatica === valor} onChange={() => alterarDidatica(valor)} />
              ))}
            </div>
            <p aria-live="polite" aria-atomic="true" className="min-h-5 text-sm text-(--muted)">
              {didatica ? `Nota selecionada: ${didatica} de 5.` : "Escolha uma nota de 1 a 5."}
            </p>
          </fieldset>
        )}

        {demaisCriterios.filter((criterio) => criterio.nome !== "recomenda").map(grupo)}
      </fieldset></div>

      {recomendacao && <div className="glass rounded-2xl! p-3 sm:p-6"><fieldset disabled={disabled} className="flex min-w-0 flex-col gap-5">
        <Cabecalho numero="02" titulo="Sua recomendação" texto="Considere sua experiência completa nesta disciplina." />
        {grupo(recomendacao)}
      </fieldset></div>}

      <p id="criterios-neutros" className="text-sm leading-relaxed text-(--muted)">
        Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim.
      </p>
    </div>
  );
}
