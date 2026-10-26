"use client";

import Link from "next/link";
import CriteriosAvaliacao from "@/components/criterios-avaliacao";
import { useRef, useState, type FormEvent } from "react";
import { criarEntradaAvaliacao, mensagemErroAvaliacao } from "@/lib/avaliacao-formulario";
import { consultarSessao } from "@/lib/services/auth";
import { enviarAvaliacao } from "@/lib/services/avaliacoes";
import { ApiError } from "@/lib/services/http-error";
import { caminhoAvaliacao } from "@/lib/retorno-avaliacao";

export default function AvaliacaoForm({ professorId, disciplinaId, retornoHref }: {
  professorId: string;
  disciplinaId: string;
  retornoHref: string;
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
      <div className="flex flex-col items-start gap-2">
        <p className="text-sm text-foreground/70">
          Você pode entrar antes de preencher. Para enviar, é necessário ter uma sessão ativa e confirmar seu e-mail institucional.
        </p>
        <Link
          href={`/login?returnTo=${encodeURIComponent(retornoHref)}`}
          className="rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium text-accent transition hover:border-foreground/40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Entrar ou criar conta antes de avaliar
        </Link>
      </div>
      <CriteriosAvaliacao rotulosExplicitos disabled={enviando} onChange={() => { setSucesso(false); setErro(null); }} />
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
              <Link href={`/login?returnTo=${encodeURIComponent(caminhoAvaliacao(professorId, disciplinaId))}`} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block font-medium text-accent underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
                Entrar na conta (nova aba)
              </Link>
            )}
          </div>
        )}
      </div>
    </form>
  );
}
