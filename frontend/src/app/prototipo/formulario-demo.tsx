"use client";

import { useState, type FormEvent } from "react";
import CriteriosAvaliacao from "@/components/criterios-avaliacao";
import { criarEntradaAvaliacao } from "@/lib/avaliacao-formulario";

export default function FormularioDemo({ professorId, disciplinaId }: {
  professorId: string;
  disciplinaId: string;
}) {
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [nota, setNota] = useState<number | null>(null);

  function revisar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    try {
      criarEntradaAvaliacao(new FormData(evento.currentTarget), professorId, disciplinaId);
      setMensagem("Prévia conferida. Nenhuma avaliação foi enviada ou salva. No sistema, o envio exige sessão autenticada e e-mail confirmado.");
    } catch (erro) {
      setMensagem(erro instanceof Error ? erro.message : "Revise as opções da avaliação.");
    }
  }

  return (
    <form onSubmit={revisar} className="flex flex-col gap-6 rounded-xl border border-foreground/10 p-5">
      <p className="text-sm text-foreground/70">
        Preencha os cinco critérios sobre a disciplina indicada acima.
      </p>
      <fieldset className="min-w-0 rounded-lg bg-accent/5 p-4" aria-describedby="didatica-demo-ajuda">
        <legend className="text-base font-semibold">Didática</legend>
        <p id="didatica-demo-ajuda" className="text-sm text-foreground/70">Como você avalia a didática deste professor? Escolha uma nota de 1 a 5.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {[1, 2, 3, 4, 5].map((valor) => <label key={valor} className="cursor-pointer">
            <input type="radio" name="didatica" value={valor} required checked={nota === valor}
              onChange={() => { setNota(valor); setMensagem(null); }} className="peer sr-only" aria-label={`Didática: nota ${valor} de 5`} />
            <span className="flex min-h-12 min-w-12 items-center justify-center rounded-lg border border-foreground/20 bg-background px-2 py-2 text-sm peer-checked:border-accent peer-checked:bg-accent/10 peer-checked:font-bold peer-focus-visible:outline-2 peer-focus-visible:outline-offset-4 peer-focus-visible:outline-accent">
              <span aria-hidden="true">{valor}</span>
            </span>
          </label>)}
        </div>
        <p aria-live="polite" className="mt-3 text-sm text-foreground/70">{nota === null ? "Nenhuma nota selecionada." : `Nota selecionada: ${nota} de 5.`}</p>
      </fieldset>
      <section className="flex flex-col gap-4" aria-label="Sobre as aulas e sua recomendação">
        <h2 className="text-base font-semibold">Sobre as aulas e sua recomendação</h2>
        <CriteriosAvaliacao rotulosExplicitos ocultarDidatica onChange={() => setMensagem(null)} />
      </section>
      <button type="submit" className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent hover:opacity-90">
        Conferir prévia da avaliação
      </button>
      <p aria-live="polite" aria-atomic="true" className="text-sm text-foreground/70">{mensagem}</p>
    </form>
  );
}
