"use client";

import { useEffect, useRef, useState } from "react";
import type { Agradecimento } from "@/lib/types/denuncia";
import {
  confirmarAgradecimentoExibido,
  listarAgradecimentos,
} from "@/lib/services/denuncias";

export default function AvisoAgradecimento() {
  const [mensagens, setMensagens] = useState<Agradecimento[]>([]);
  const exibidosRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    let cancelado = false;
    const controlador = new AbortController();

    async function buscarEConfirmar() {
      try {
        const lista = await listarAgradecimentos(controlador.signal);
        if (cancelado || lista.length === 0) return;

        setMensagens(lista);

        // Confirma a exibição de cada mensagem uma única vez
        for (const item of lista) {
          if (!exibidosRef.current.has(item.id)) {
            exibidosRef.current.add(item.id);
            confirmarAgradecimentoExibido(item.id, controlador.signal).catch(() => {
              // Falha silenciosa na confirmação de exibição não quebra a tela
            });
          }
        }
      } catch {
        // Ignora erros para não interromper navegação do usuário
      }
    }

    void buscarEConfirmar();

    return () => {
      cancelado = true;
      controlador.abort();
    };
  }, []);

  const dispensar = (id: string) => {
    setMensagens((atuais) => atuais.filter((m) => m.id !== id));
  };

  if (mensagens.length === 0) return null;

  return (
    <div
      aria-label="Avisos de agradecimento da moderação"
      className="mx-auto flex w-full max-w-5xl flex-col gap-2 px-4 pt-3"
    >
      {mensagens.map((item) => (
        <div
          key={item.id}
          role="status"
          data-testid={`agradecimento-${item.id}`}
          className="flex items-center justify-between gap-4 rounded-xl border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-foreground shadow-xs"
        >
          <div className="flex items-center gap-2">
            <span className="text-accent" aria-hidden="true">
              ✓
            </span>
            <p className="font-medium">{item.mensagem}</p>
          </div>
          <button
            type="button"
            onClick={() => dispensar(item.id)}
            aria-label="Dispensar agradecimento"
            className="rounded-md px-2 py-1 text-xs font-semibold text-accent hover:bg-accent/10 transition"
          >
            Entendido
          </button>
        </div>
      ))}
    </div>
  );
}
