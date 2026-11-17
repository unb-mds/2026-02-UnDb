"use client";

import { useEffect, useRef, useState } from "react";
import { consultarUtilidade, definirVoto } from "@/lib/services/votos-comentario";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";
import type { UtilidadeComentario, VotoComentario } from "@/lib/types/comentario";

function mensagem(erro: unknown): string {
  if (erro instanceof ApiError) {
    if (erro.status === 401) return "Entre em uma conta estudantil confirmada para votar.";
    if (erro.status === 403) return "Confirme seu e-mail para votar. Não é permitido votar no próprio comentário.";
    if (erro.status === 404) return "Este comentário não está mais disponível para votos.";
  }
  return "Não foi possível atualizar a utilidade. Tente novamente.";
}

export default function UtilidadeDoComentario({ versaoId }: { versaoId: string }) {
  const [resumo, setResumo] = useState<UtilidadeComentario | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [consulta, setConsulta] = useState(0);
  const requisicao = useRef<AbortController | null>(null);
  const ocupada = useRef(false);

  useEffect(() => {
    let ativa = true;
    const carregar = () => {
      requisicao.current?.abort();
      const controller = new AbortController();
      requisicao.current = controller;
      ocupada.current = true;
      setResumo(null);
      setErro("");
      setCarregando(true);
      consultarUtilidade(versaoId, controller.signal).then((dados) => {
        if (ativa && !controller.signal.aborted) setResumo(dados);
      }).catch((e: unknown) => {
        if (ativa && !controller.signal.aborted) setErro(mensagem(e));
      }).finally(() => {
        if (ativa && !controller.signal.aborted) {
          ocupada.current = false;
          setCarregando(false);
        }
      });
    };
    carregar();
    window.addEventListener(EVENTO_SESSAO_ALTERADA, carregar);
    return () => {
      ativa = false;
      requisicao.current?.abort();
      window.removeEventListener(EVENTO_SESSAO_ALTERADA, carregar);
    };
  }, [versaoId, consulta]);

  async function votar(voto: VotoComentario) {
    if (ocupada.current || !resumo) return;
    ocupada.current = true;
    const controller = new AbortController();
    requisicao.current = controller;
    setCarregando(true);
    setErro("");
    try {
      const dados = await definirVoto(versaoId, resumo.meu_voto === voto ? null : voto, controller.signal);
      if (!controller.signal.aborted) setResumo(dados);
    } catch (e) {
      if (!controller.signal.aborted) setErro(mensagem(e));
    } finally {
      if (!controller.signal.aborted) {
        ocupada.current = false;
        setCarregando(false);
      }
    }
  }

  return (
    <div role="group" aria-label="Este comentário foi útil?" aria-busy={carregando} className="flex flex-col gap-2">
      <p className="text-sm text-foreground">Este comentário foi útil?</p>
      {resumo && <div className="flex flex-wrap gap-2">
        {([ ["UTIL", "Útil", resumo.uteis], ["NAO_UTIL", "Não útil", resumo.nao_uteis] ] as const).map(([voto, label, total]) => (
          <button key={voto} type="button" className="button min-h-11 gap-2"
            aria-pressed={resumo.meu_voto === voto} disabled={carregando} onClick={() => votar(voto)}>
            {resumo.meu_voto === voto && <span aria-hidden="true">✓</span>}{label} ({total})
          </button>
        ))}
      </div>}
      {resumo?.meu_voto && <p className="text-sm text-[var(--muted)]">Selecione o voto marcado novamente para retirá-lo.</p>}
      <p role="status" className="text-sm text-[var(--muted)]">{carregando ? "Atualizando utilidade…" : ""}</p>
      {erro && <p role="alert" className="text-sm text-[var(--danger)]">{erro}</p>}
      {!resumo && !carregando && <button type="button" className="button self-start" onClick={() => setConsulta((v) => v + 1)}>Tentar novamente</button>}
    </div>
  );
}
