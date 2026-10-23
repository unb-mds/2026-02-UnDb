"use client";

import { useState, type FormEvent } from "react";
import CriteriosAvaliacao from "@/components/criterios-avaliacao";
import { criarEntradaAvaliacao } from "@/lib/avaliacao-formulario";

export default function FormularioDemo({ professorId, disciplinaId }: {
  professorId: string;
  disciplinaId: string;
}) {
  const [mensagem, setMensagem] = useState<string | null>(null);

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
    <form onSubmit={revisar} className="flex flex-col gap-6">
      <p className="text-sm text-foreground/70">
        Preencha os cinco critérios sobre a disciplina indicada acima.
      </p>
      <CriteriosAvaliacao rotulosExplicitos onChange={() => setMensagem(null)} />
      <button type="submit" className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent hover:opacity-90">
        Conferir prévia da avaliação
      </button>
      <p aria-live="polite" aria-atomic="true" className="text-sm text-foreground/70">{mensagem}</p>
    </form>
  );
}
