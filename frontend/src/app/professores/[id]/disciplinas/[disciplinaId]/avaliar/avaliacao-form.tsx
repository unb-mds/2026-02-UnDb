"use client";

import Link from "next/link";
import { useRef, useState, type FormEvent } from "react";
import { criteriosAvaliacao, criarEntradaAvaliacao, mensagemErroAvaliacao } from "@/lib/avaliacao-formulario";
import { consultarSessao } from "@/lib/services/auth";
import { enviarAvaliacao } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";

export default function AvaliacaoForm({ professorId, disciplinaId }: {
  professorId: string;
  disciplinaId: string;
}) {
  const enviandoRef = useRef(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [precisaEntrar, setPrecisaEntrar] = useState(false);
  const [sucesso, setSucesso] = useState(false);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviandoRef.current) return;
    setErro(null);
    setSucesso(false);
    setPrecisaEntrar(false);

    let dados;
    try {
      dados = criarEntradaAvaliacao(new FormData(evento.currentTarget), professorId, disciplinaId);
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Revise as opções da avaliação.");
      return;
    }

    enviandoRef.current = true;
    setEnviando(true);
    try {
      const sessao = await consultarSessao();
      if (!sessao.autenticado) {
        throw new ApiError("É necessário autenticar-se para registrar uma avaliação.", 401);
      }
      await enviarAvaliacao(dados);
      setSucesso(true);
    } catch (falha) {
      setPrecisaEntrar(falha instanceof ApiError && falha.status === 401);
      setErro(mensagemErroAvaliacao(falha));
    } finally {
      enviandoRef.current = false;
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} className="flex flex-col gap-6" aria-busy={enviando}>
      <p className="text-sm text-foreground/70">
        Responda aos cinco critérios. Para enviar, entre na sua conta e confirme seu e-mail institucional.
      </p>
      <fieldset disabled={enviando} className="flex min-w-0 flex-col gap-4">
        <legend className="sr-only">Critérios da avaliação</legend>
        {criteriosAvaliacao.map((criterio) => (
          <label key={criterio.nome} className="flex min-w-0 flex-col gap-2">
            <span className="text-sm font-medium">{criterio.rotulo}</span>
            <select
              name={criterio.nome}
              required
              defaultValue=""
              onChange={() => { setSucesso(false); setErro(null); }}
              aria-describedby={criterio.nome === "dificuldade" || criterio.nome === "chamada" ? "criterios-neutros" : undefined}
              className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base outline-none focus:border-foreground/50"
            >
              <option value="" disabled>Selecione uma opção</option>
              {criterio.opcoes.map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
            </select>
          </label>
        ))}
      </fieldset>
      <p id="criterios-neutros" className="text-sm text-foreground/70">
        Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim.
      </p>
      <button
        type="submit"
        disabled={enviando}
        className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {enviando ? "Enviando…" : "Enviar avaliação"}
      </button>
      <div aria-live="polite" aria-atomic="true">
        {sucesso && (
          <p role="status" className="rounded-lg border border-green-600/30 bg-green-600/10 p-4 text-sm">
            Avaliação registrada com sucesso. Se você já tinha uma avaliação para este professor nesta disciplina, ela foi substituída por este envio.
          </p>
        )}
        {erro && (
          <div role="alert" className="rounded-lg border border-red-600/30 bg-red-600/10 p-4 text-sm">
            <p>{erro}</p>
            {precisaEntrar && (
              <Link href="/login" target="_blank" rel="noopener noreferrer" className="mt-2 inline-block font-medium text-accent underline underline-offset-4">
                Entrar na conta (nova aba)
              </Link>
            )}
          </div>
        )}
      </div>
    </form>
  );
}
