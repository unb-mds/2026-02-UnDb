import { criteriosAvaliacao } from "@/lib/avaliacao-formulario";

export default function CriteriosAvaliacao({ disabled = false, onChange, rotulosExplicitos = false }: {
  disabled?: boolean;
  onChange?: () => void;
  rotulosExplicitos?: boolean;
}) {
  return (
    <>
      <fieldset disabled={disabled} className="flex min-w-0 flex-col gap-4">
        <legend className="sr-only">Critérios da avaliação</legend>
        {criteriosAvaliacao.map((criterio) => (
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
                  : rotulosExplicitos && criterio.nome === "recomenda"
                    ? valor === "true" ? "Recomenda a matéria" : "Não recomenda a matéria"
                    : rotulo}
              </option>)}
            </select>
          </label>
        ))}
      </fieldset>
      <p id="criterios-neutros" className="text-sm text-foreground/70">
        Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim.
      </p>
    </>
  );
}
