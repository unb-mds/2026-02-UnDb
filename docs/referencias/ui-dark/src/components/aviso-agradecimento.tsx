"use client";

import { useEffect, useRef, useState } from "react";
import type { Agradecimento } from "@/lib/types/denuncia";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { confirmarAgradecimentoExibido, listarAgradecimentos } from "@/lib/services/denuncias";

function MensagemAgradecimento({ item, dispensar }: {
  item: Agradecimento;
  dispensar: (id: string) => void;
}) {
  const elemento = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controlador = new AbortController();
    let visivel = false;
    let enviando = false;
    let confirmado = false;
    const confirmar = () => {
      if (!visivel || document.visibilityState !== "visible" || enviando || confirmado) return;
      enviando = true;
      void confirmarAgradecimentoExibido(item.id, controlador.signal)
        .then(() => { confirmado = true; })
        .catch(() => { /* Mantém a mensagem no servidor; foco/visibilidade permitem nova tentativa. */ })
        .finally(() => { enviando = false; });
    };
    const observador = new IntersectionObserver(([entrada]) => {
      visivel = entrada.isIntersecting;
      confirmar();
    });
    if (elemento.current) observador.observe(elemento.current);
    document.addEventListener("visibilitychange", confirmar);
    window.addEventListener("focus", confirmar);
    return () => {
      controlador.abort();
      observador.disconnect();
      document.removeEventListener("visibilitychange", confirmar);
      window.removeEventListener("focus", confirmar);
    };
  }, [item.id]);

  return (
    <div ref={elemento} role="status" data-testid={`agradecimento-${item.id}`}
      className="flex items-center justify-between gap-4 rounded-xl border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-foreground shadow-xs">
      <div className="flex items-center gap-2">
        <span className="text-accent" aria-hidden="true">✓</span>
        <p className="font-medium">{item.mensagem}</p>
      </div>
      <button type="button" onClick={() => dispensar(item.id)} aria-label="Dispensar agradecimento"
        className="rounded-md px-2 py-1 text-xs font-semibold text-accent hover:bg-accent/10 transition">
        Entendido
      </button>
    </div>
  );
}

export default function AvisoAgradecimento() {
  return <AvisosDaConta />;
}

function AvisosDaConta() {
  const [lote, setLote] = useState<{ geracao: number; mensagens: Agradecimento[] }>({ geracao: 0, mensagens: [] });

  useEffect(() => {
    let geracao = 0;
    let controlador: AbortController;
    const buscar = () => {
      controlador?.abort();
      controlador = new AbortController();
      const atual = ++geracao;
      setLote({ geracao: atual, mensagens: [] });
      void listarAgradecimentos(controlador.signal).then((mensagens) => {
        if (atual === geracao && !controlador.signal.aborted) setLote({ geracao: atual, mensagens });
      }).catch(() => { /* Sem dados privados antigos quando sessão ou consulta falha. */ });
    };
    buscar();
    window.addEventListener(EVENTO_SESSAO_ALTERADA, buscar);
    return () => {
      ++geracao;
      controlador.abort();
      window.removeEventListener(EVENTO_SESSAO_ALTERADA, buscar);
    };
  }, []);

  const dispensar = (id: string) => {
    setLote((atual) => ({ ...atual, mensagens: atual.mensagens.filter((m) => m.id !== id) }));
  };
  if (lote.mensagens.length === 0) return null;
  return (
    <div aria-label="Avisos de agradecimento da moderação" className="mx-auto flex w-full max-w-5xl flex-col gap-2 px-4 pt-3">
      {lote.mensagens.map((item) => (
        <MensagemAgradecimento key={`${lote.geracao}:${item.id}`} item={item} dispensar={dispensar} />
      ))}
    </div>
  );
}
