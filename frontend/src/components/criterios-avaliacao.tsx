"use client";

import { useState } from "react";
import { criteriosAvaliacao } from "@/lib/avaliacao-formulario";

export default function CriteriosAvaliacao({ disabled = false, onChange, rotulosExplicitos = false, ocultarDidatica = false }: {
  disabled?: boolean;
  onChange?: () => void;
  rotulosExplicitos?: boolean;
  ocultarDidatica?: boolean;
}) {
  const [didatica, setDidatica] = useState("");
  const criterioDidatica = criteriosAvaliacao[0];
  const demaisCriterios = criteriosAvaliacao.slice(1);

  function alterarDidatica(valor: string) {
    setDidatica(valor);
    onChange?.();
  }

  return (
    <div className="flex flex-col gap-6">
      <fieldset disabled={disabled} className="flex min-w-0 flex-col gap-4">
        <legend className="text-lg font-semibold">Sobre as aulas</legend>

        {!ocultarDidatica && (
          <fieldset className="flex min-w-0 flex-col gap-2">
            <legend className="text-sm font-medium">Didática</legend>
            <div className="flex flex-wrap gap-2" aria-label="Nota de Didática">
              {criterioDidatica.opcoes.map(([valor, rotulo]) => (
                <label key={valor} className="cursor-pointer">
                  <input
                    className="peer sr-only"
                    type="radio"
                    name="didatica"
                    value={valor}
                    checked={didatica === valor}
                    required
                    onChange={() => alterarDidatica(valor)}
                  />
                  <span className="flex h-12 min-w-12 items-center justify-center rounded-lg border border-foreground/20 px-4 text-base font-semibold transition hover:border-foreground/40 peer-checked:border-accent peer-checked:bg-accent/10 peer-checked:text-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2">
                    {rotulo}
                  </span>
                </label>
              ))}
            </div>
            <p aria-live="polite" aria-atomic="true" className="min-h-5 text-sm text-foreground/70">
              {didatica ? `Nota selecionada: ${didatica} de 5.` : "Escolha uma nota de 1 a 5."}
            </p>
          </fieldset>
        )}

        {demaisCriterios.filter((criterio) => criterio.nome !== "recomenda").map((criterio) => (
          <label key={criterio.nome} className="flex min-w-0 flex-col gap-2">
            <span className="text-sm font-medium">{rotulosExplicitos && criterio.nome === "chamada" ? "O professor faz chamada?" : criterio.rotulo}</span>
            <select
              name={criterio.nome}
              required
              defaultValue=""
              onChange={onChange}
              aria-describedby={criterio.nome === "dificuldade" || criterio.nome === "chamada" ? "criterios-neutros" : undefined}
              className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base focus:border-foreground/50 focus-visible:ring-2 focus-visible:ring-accent"
            >
              <option value="" disabled>Selecione uma opção</option>
              {criterio.opcoes.map(([valor, rotulo]) => <option key={valor} value={valor}>
                {rotulosExplicitos && criterio.nome === "chamada"
                  ? valor === "true" ? "Faz chamada" : "Não faz chamada"
                  : rotulo}
              </option>)}
            </select>
          </label>
        ))}
      </fieldset>

      <fieldset disabled={disabled} className="flex min-w-0 flex-col gap-2">
        <legend className="text-lg font-semibold">Sua recomendação</legend>
        {demaisCriterios.filter((criterio) => criterio.nome === "recomenda").map((criterio) => (
          <label key={criterio.nome} className="flex min-w-0 flex-col gap-2">
            <span className="text-sm font-medium">{criterio.rotulo}</span>
            <select name={criterio.nome} required defaultValue="" onChange={onChange} className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base focus:border-foreground/50 focus-visible:ring-2 focus-visible:ring-accent">
              <option value="" disabled>Selecione uma opção</option>
              {criterio.opcoes.map(([valor, rotulo]) => <option key={valor} value={valor}>
                {rotulosExplicitos
                  ? valor === "true" ? "Recomendo" : "Não recomendo"
                  : rotulo}
              </option>)}
            </select>
          </label>
        ))}
      </fieldset>

      <p id="criterios-neutros" className="text-sm text-foreground/70">
        Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim.
      </p>
    </div>
  );
}
